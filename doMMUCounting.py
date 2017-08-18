import os
import sys
import time
import json
import numpy
import report_mmu
from datetime import datetime

# import GDAL/OGR modules
try:
    from osgeo import ogr, gdal, osr
except ImportError:
    import ogr
    import gdal
    import osr

numpy.seterr(divide='ignore', invalid='ignore')

def tmpdir():
    if 'TMPDIR' in os.environ:
        return os.environ['TMPDIR']
    if 'TMP' in os.environ:
        return os.environ['TMP']
    if 'tmp' in os.environ:
        return os.environ['tmp']
    if 'temp' in os.environ:
        return os.environ['temp']
    if 'tmpdir' in os.environ:
        return os.environ['tmpdir']


def toLonLat(pointX, pointY, inSpatialRefWkt, outputEPSG=4326):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(pointX, pointY)
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromWkt( inSpatialRefWkt )
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputEPSG)
    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    point.Transform(coordTransform)

    return point.GetX(), point.GetY()

def mapToPixel(mx, my, gt):
    if gt[2] + gt[4] == 0:  # Simple calc, no inversion required
        px = (mx - gt[0]) / gt[1]
        py = (my - gt[3]) / gt[5]
    else:
        px, py = ApplyGeoTransform(mx, my, InvGeoTransform(gt))
    return int(px + 0.5), int(py + 0.5)

def pixelToMap(px, py, gt):
    mx, my = ApplyGeoTransform(px, py, gt)
    return mx, my

def ApplyGeoTransform(inx, iny, gt):
    ''' Apply a geotransform
        @param  inx       Input x coordinate (double)
        @param  iny       Input y coordinate (double)
        @param  gt        Input geotransform (six doubles)
        @return outx,outy Output coordinates (two doubles)
    '''
    outx = gt[0] + inx * gt[1] + iny * gt[2]
    outy = gt[3] + inx * gt[4] + iny * gt[5]
    return (outx, outy)

def InvGeoTransform(gt_in):
    # we assume a 3rd row that is [1 0 0]
    # Compute determinate
    det = gt_in[1] * gt_in[5] - gt_in[2] * gt_in[4]

    if (abs(det) < 0.000000000000001):
        return

    inv_det = 1.0 / det

    # compute adjoint, and divide by determinate
    gt_out = [0, 0, 0, 0, 0, 0]
    gt_out[1] = gt_in[5] * inv_det
    gt_out[4] = -gt_in[4] * inv_det

    gt_out[2] = -gt_in[2] * inv_det
    gt_out[5] = gt_in[1] * inv_det

    gt_out[0] = (gt_in[2] * gt_in[3] - gt_in[0] * gt_in[5]) * inv_det
    gt_out[3] = (-gt_in[1] * gt_in[3] + gt_in[0] * gt_in[4]) * inv_det

    return gt_out

# alignToImg: warp image imgToAlign onto imgRef, to get a superimposable grid.
# imgRef: filename, reference file
# imgToAlign: filename, image to warp onto imgRef
# aligned: filename, warp result
# resampleType: warp algorithm, see gdal.Warp documentation
def alignToImg(imgRef, imgToAlign, aligned,resampleType):
    refFid = gdal.Open(imgRef, gdal.GA_ReadOnly)
    ns = refFid.RasterXSize
    nl = refFid.RasterYSize
    gt = refFid.GetGeoTransform()
    proj = refFid.GetProjection()
    ul = pixelToMap(0,0,gt)
    lr = pixelToMap(ns, nl, gt)
    outputBounds = ( min(ul[0], lr[0]), min(ul[1],lr[1]), max(ul[0],lr[0]), max(ul[1],lr[1]) )

    try:
        gdal.Warp(aligned, imgToAlign, dstSRS=proj, dstNodata=0,
                  outputBounds=outputBounds, outputBoundsSRS=proj,
                  xRes=abs(gt[1]), yRes=abs(gt[5]),
                  resampleAlg=resampleType, format='Gtiff', options=['compress=lzw','bigtiff=IF_SAFER'])
    except:
        return -1
    return 0

# reproject a shapefile to targetSRS. If the shp SRS is unknown, assume EPSG:4326
# save result to "fileOut"
# return True for success, False otherwise
def reprojShp(shp, targetSRS, fileOut):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # input SpatialReference
    dataSource = driver.Open(shp, 0)
    layer = dataSource.GetLayer()
    spatialRef = layer.GetSpatialRef()
    if spatialRef is None or spatialRef=='':
        spatialRef = osr.SpatialReference()
        spatialRef.ImportFromEPSG(4326)
        
    coordTrans = osr.CoordinateTransformation(spatialRef, targetSRS)
    deleteFile(fileOut)
    try:
        if os.path.exists(fileOut):
            driver.DeleteDataSource(fileOut)
    except Exception, e:
        return False
    outDS = driver.CreateDataSource(fileOut)
    outLayer = outDS.CreateLayer("disagTMP", targetSRS, geom_type=ogr.wkbMultiPolygon)
    # add fields
    inLayerDefn = layer.GetLayerDefn()
    for ii in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(ii)
        outLayer.CreateField(fieldDefn)
    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()
    # loop through the input features
    inFeature = layer.GetNextFeature()
    while inFeature:
        geom = inFeature.GetGeometryRef() # get the input geometry
        geom.Transform(coordTrans) # reproject the geometry
        outFeature = ogr.Feature(outLayerDefn) # create a new feature
        outFeature.SetGeometry(geom) # set the geometry and attribute
        for ii in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(ii).GetNameRef(), inFeature.GetField(ii))
        outLayer.CreateFeature(outFeature) # add the feature to the shapefile
        outFeature = None # dereference the features and get the next input feature
        inFeature = layer.GetNextFeature()

    # Save and close the shapefiles
    dataSource = None
    outDS = None

    return True

#
# Count uniq values in an image, returns area for each uniq value
#
def uniqValCountRaster(img, sqrps_ha):
    fid = gdal.Open(img, gdal.GA_ReadOnly)
    ns = fid.RasterXSize
    nl = fid.RasterYSize
    uniq=numpy.array([])
    for il in xrange(nl):
        uniq = numpy.append(uniq, numpy.unique(numpy.ravel(fid.GetRasterBand(1).ReadAsArray(0, il, ns, 1))))

    # count uniq occurences
    countUniq = {}
    for ii in uniq:
        countUniq[ii] = 0

    # compute number of pixel for each uniq
    for ii in countUniq:
        for il in xrange(nl):
            thisData = numpy.ravel(fid.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
            countUniq[ii] += numpy.array(thisData == ii).astype(int).sum()
        countUniq[ii] *= sqrps_ha

    return countUniq

# returns list of unique values for field, and associated integer
def rasterizeDisag(shp, field, refImage, cellSize, disagMap):
    # create an empty image, identical to refImage
    refFid = gdal.Open(refImage, gdal.GA_ReadOnly)
    ns = refFid.RasterXSize / cellSize
    nl = refFid.RasterYSize / cellSize
    gt = refFid.GetGeoTransform()
    newGt = (gt[0], cellSize * gt[1], gt[2], gt[3], gt[4], cellSize*gt[5])
    proj = refFid.GetProjection()
    projRef = refFid.GetProjectionRef()
    targetSRS = osr.SpatialReference()
    #targetSRS.CloneGeogCS(projRef)
    targetSRS.ImportFromWkt(projRef)
    refFid = None

    if not(test_overlapping(shp, refImage)):
        return False

    # resolve overlapping issues
    shpClean = shp
    # shpClean = os.path.join(GLOBALS['temp_path'], os.path.basename(shp))
    # print 'cleaning topo'
    # os.system(
    #     'ogr2ogr ' + shpClean + ' ' + shp + ' -dialect sqlite -sql "SELECT ST_Union(geometry) AS geometry FROM \'' + os.path.basename(
    #         shp).replace('.shp', '') + '\'"')
    # print 'done'


    # reproject shp into target raster SRS
    tmpShp = os.path.join( tmpdir(), '{}_disag.shp'.format( os.path.basename(shp) ))
    reprojShp(shpClean, targetSRS, tmpShp)

    outDs = gdal.GetDriverByName('GTiff').Create(disagMap, ns, nl, 1, gdal.GDT_Int16, options=['compress=lzw','bigtiff=IF_SAFER'])
    outDs.SetGeoTransform(newGt)
    outDs.SetProjection( proj )

    # set default to -1
    lineDefault = numpy.zeros((1,ns)) - 1
    for il in xrange(nl):
        outDs.GetRasterBand(1).WriteArray(lineDefault, 0, il)

    # get shapefile information
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(tmpShp, 0)
    # assume n layers
    layer = dataSource.GetLayer()
    try:
        uniqValues = list(set([feature.GetFieldAsString(field) for feature in layer]))
    except Exception, e:
        return False
    if uniqValues == []:
        return False
    #dataSource = None  # must be closed

    classes = {-1:"Other"}
    try:
        for ii in range(len(uniqValues)):
            classes[ii]=uniqValues[ii]
            # select features
            layer.SetAttributeFilter( "{} = '{}'".format(field, uniqValues[ii]) )
            gdal.RasterizeLayer(outDs, [1], layer, burn_values = [ii] )

            # options = gdal.RasterizeOptions(format='gtiff', where='"{}"="{}"'.format(field, uniqValues[ii]),
            #                                 xRes=newGt[1], yRes=newGt[5], outputSRS=projRef,
            #                                 width=ns, height=nl,
            #                                 layers=["disagTMP"],
            #                                 burnValues=[ii],
            #                                 #bands=[1]
            #                                 )
            # gdal.RasterizeLayer(outDs, [1], tmpShp, ["disagTMP"], options=options)
    except Exception, e:
        return False

    dataSource = None
    return classes
# ___________________
# try deleting a file
# ___________________
def deleteFile(thisFile):
    try:
        os.remove(thisFile)
    except:
        return False
    return True

# ____________________
# Create the report output
# ____________________
def getTemplate(useConversionMapBool, inputFile, conversionMapFile, LANG, FTOT, NFTOT, FNF1TOT, FNF2TOT, NDTOT, PXPTOT, EMDefP1, EMDefP2, EMDegP1, EMDegP2, EMDisag, useExceptMapBool, uniqExceptCount, psize,  startYY1, endYY1, startYY2, endYY2, CLASSTOT, kernel_size, biomass_value, degradationPercent, forestThreshold, ULX, ULY, LRX, LRY):
    deltaYY1 = endYY1-startYY1 + 1
    deltaYY2 = endYY2-startYY2 + 1
    if deltaYY1 > 1:
        yearP1={'EN':'years','FR':'ans','PT':'anos'}
        yearDur1={'EN': 'the period from {} to {}'.format(startYY1, endYY1), 'FR':'la p&eacute;riode de {} &agrave; {}'.format(startYY1, endYY1), 'PT':'{} a {}'.format(startYY1, endYY1) }
    else:
        yearP1 = {'EN': 'year', 'FR': 'an', 'PT': 'ano'}
        yearDur1= {'EN':'the year {}'.format(startYY1), 'FR':"l'ann&eacute;e {}".format(startYY1), 'PT':'a {}'.format(startYY1)}
    if deltaYY2 > 1:
        yearP2={'EN':'years','FR':'ans','PT':'anos'}
        yearDur2={'EN':'the period from {} to {}'.format(startYY2, endYY2), 'FR':'la p&eacute;riode de {} &agrave; {}'.format(startYY2, endYY2), 'PT':'{} a {}'.format(startYY2, endYY2)}
    else:
        yearP2 ={'EN': 'year', 'FR': 'an', 'PT': 'ano'}
        yearDur2 = {'EN': 'the year {}'.format(startYY2), 'FR': "&agrave; l'ann&eacute;e {}".format(startYY2), 'PT': "a l'ano {}".format(startYY2)}
    sqrps_ha = psize*psize*1./10000.0 # gives the size of a pixel in ha
    bxsize_ha = kernel_size * kernel_size * psize * psize * 1.0 / 10000.0 # box size in ha
    biomass_valuePx  = biomass_value * sqrps_ha # biomass_value is read from the interface: value per ha, biomass_valuePx is the biomass factor per pixel
    toEqCo2 = 1.0 / 0.2727  # factor to convert tC into tEqCO2

    totalPXPTOT = 0

    # string for disaggregated values
    thisDisagString=''
    if EMDisag['useDisagShpBool']:
        try:
            thisDisagString = report_mmu.disagString(LANG, EMDisag, toEqCo2)
            exceptionIndex=3
        except Exception, e:
            pass
    # string for exceptions
    thisExceptString=''
    if useExceptMapBool:
        thisExceptString = report_mmu.exceptString(LANG, uniqExceptCount)

    LANG = LANG.upper() # force upper case

    if LANG in ['EN','FR', 'PT']:
        if useConversionMapBool: # when using the bionmass map
            fromMap={'EN':'from map', 'FR':'de la carte','PT':'from map'}
            conversionFactorMap = ' {} {} (in tC/Ha)'.format(fromMap[LANG], conversionMapFile)

            template = '<html>' + report_mmu.head[LANG] + '<body>' + \
                       report_mmu.report_head[LANG].format(deltaYY1, yearP1[LANG], yearDur1[LANG], deltaYY2, yearP2[LANG], yearDur2[LANG], conversionFactorMap,
                                                                   bxsize_ha, int(forestThreshold * 100), os.path.basename(inputFile),time.strftime("%d/%m/%Y"), ULX, ULY, LRX, LRY,
                                                                   degradationPercent) + \
                       '<h1>RESULTS</h1>' + \
                       report_mmu.report_section_per_MMU_pixel[LANG].format(PXPTOT['Deforest_p1'] * sqrps_ha, PXPTOT['Degrad_p1'] * sqrps_ha, PXPTOT['Deforest_p1'] * sqrps_ha / deltaYY1,
                                                                                    PXPTOT['Degrad_p1'] * sqrps_ha / deltaYY1, \
                                                                                    PXPTOT['Deforest_p2'] * sqrps_ha,PXPTOT['Degrad_p2'] * sqrps_ha, PXPTOT['Deforest_p2'] * sqrps_ha / deltaYY2,
                                                                                    PXPTOT['Degrad_p2'] * sqrps_ha / deltaYY2, \
                                                                                    startYY1, (PXPTOT['Deforest_p1'] + PXPTOT['Deforest_p2'] + PXPTOT['Degrad_p1'] + PXPTOT['Degrad_p2'] + PXPTOT['FF_10'] +
                                                                                    PXPTOT['FF_2x'] + PXPTOT['FF_3x']) * sqrps_ha) + \
                       '<br/>' + \
                        thisDisagString +\
                        thisExceptString +\
                       report_mmu.report_section_per_MMU[LANG].format(
                           (CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha, CLASSTOT['31'] * bxsize_ha,
                           (CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha / deltaYY1,
                           CLASSTOT['31'] * bxsize_ha / deltaYY1, \
                           (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha, CLASSTOT['32'] * bxsize_ha,
                           (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha / deltaYY2,
                           CLASSTOT['32'] * bxsize_ha / deltaYY2, \
                           EMDefP1 * toEqCo2, EMDegP1 * toEqCo2, EMDefP1 * toEqCo2 / deltaYY1, EMDegP1 * toEqCo2 / deltaYY1, \
                           EMDefP2 * toEqCo2, EMDegP2 * toEqCo2, EMDefP2 * toEqCo2 / deltaYY2, EMDegP2 * toEqCo2 / deltaYY2,
                           startYY1, (CLASSTOT['21'] + CLASSTOT['24'] + CLASSTOT['22'] + CLASSTOT['23'] + CLASSTOT['31'] +
                           CLASSTOT['32'] + CLASSTOT['33'] + CLASSTOT['10']) * bxsize_ha, \
                           CLASSTOT['33'] * bxsize_ha) + \
                       '</body> </html>'
        else: # when using the constant emission factor
            template = '<html>' + report_mmu.head[LANG] + '<body>' + \
                  report_mmu.report_head[LANG].format(deltaYY1, yearP1[LANG], yearDur1[LANG], deltaYY2, yearP2[LANG], yearDur2[LANG], ': {} ({} tEqCo<sub>2</sub>)'.format(biomass_value, biomass_value * toEqCo2), bxsize_ha, int(forestThreshold*100), os.path.basename(inputFile), time.strftime("%d/%m/%Y"), ULX, ULY, LRX, LRY,
                                                              degradationPercent) + \
                  '<h1>RESULTS</h1>' + \
                  report_mmu.report_section_per_MMU_pixel[LANG].format(PXPTOT['Deforest_p1']*sqrps_ha, PXPTOT['Degrad_p1']*sqrps_ha, PXPTOT['Deforest_p1']*sqrps_ha/deltaYY1, PXPTOT['Degrad_p1']*sqrps_ha/deltaYY1, \
                                                                               PXPTOT['Deforest_p2'] * sqrps_ha, PXPTOT['Degrad_p2']*sqrps_ha, PXPTOT['Deforest_p2']*sqrps_ha/deltaYY2, PXPTOT['Degrad_p2']*sqrps_ha/deltaYY2, \
                                                                               startYY1, (PXPTOT['Deforest_p1'] + PXPTOT['Deforest_p2'] + PXPTOT['Degrad_p1'] + PXPTOT['Degrad_p2'] + PXPTOT['FF_10'] + PXPTOT['FF_2x'] + PXPTOT['FF_3x'] ) * sqrps_ha) +\
                  '<br/>' + \
                  thisDisagString + \
                  thisExceptString + \
                  report_mmu.report_section_per_MMU[LANG].format((CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha, CLASSTOT['31'] * bxsize_ha, (CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha/deltaYY1, CLASSTOT['31'] * bxsize_ha/deltaYY1, \
                                                                         (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha, CLASSTOT['32']*bxsize_ha, (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha/deltaYY2, CLASSTOT['32']*bxsize_ha/deltaYY2, \
                                                                         PXPTOT['Deforest_p1'] * toEqCo2 * biomass_valuePx, PXPTOT['Degrad_p1'] * toEqCo2* degradationPercent * biomass_valuePx / 100.0, PXPTOT['Deforest_p1'] * toEqCo2 * biomass_valuePx / deltaYY1, PXPTOT['Degrad_p1'] * toEqCo2 * degradationPercent* biomass_valuePx/deltaYY1 / 100.0, \
                                                                         PXPTOT['Deforest_p2'] * toEqCo2 * biomass_valuePx, PXPTOT['Degrad_p2']* toEqCo2 * degradationPercent * biomass_valuePx/ 100.0, PXPTOT['Deforest_p2'] * toEqCo2 * biomass_valuePx / deltaYY2, PXPTOT['Degrad_p2'] * toEqCo2 * degradationPercent * biomass_valuePx/deltaYY2 / 100.0, \
                                                                         startYY1, (CLASSTOT['21'] + CLASSTOT['24'] + CLASSTOT['22'] + CLASSTOT['23'] + CLASSTOT['31'] + CLASSTOT['32'] + CLASSTOT['33'] + CLASSTOT['10'] )* bxsize_ha, \
                                                                         CLASSTOT['33'] * bxsize_ha) + \
                  '</body> </html>'
#                  roadless_report_en.report_section_per_MMU[LANG] + \
#                  roadless_report_en.report_conversion_px_mmu[LANG].format(PXPTOT['Deforest_p1']*sqrps_ha, PXPTOT['Deforest_p2']*sqrps_ha, PXPTOT['Degrad_p1']*sqrps_ha, PXPTOT['Degrad_p2']*sqrps_ha, (PXPTOT['FF_10'] + PXPTOT['FF_2x'] + PXPTOT['FF_3x']) * sqrps_ha, (PXPTOT['FF_4x'] + PXPTOT['NF_10'] + PXPTOT['NF_2x'] + PXPTOT['NF_3x'] + PXPTOT['NF_4x'] + PXPTOT['FNF1_4x'] + PXPTOT['FNF2_4x'])*sqrps_ha, (PXPTOT['ND_0x'] + PXPTOT['ND_1x']+PXPTOT['ND_2x']+PXPTOT['ND_3x']+PXPTOT['ND_4x'])*sqrps_ha) + \
#                  roadless_report_en.report_rates_px_mmu[LANG].format(PXPTOT['Deforest_p1']*sqrps_ha/deltaYY1, PXPTOT['Deforest_p2']*sqrps_ha/deltaYY2, PXPTOT['Degrad_p1']*sqrps_ha/deltaYY1, PXPTOT['Degrad_p2']*sqrps_ha/deltaYY2) + \
#                  roadless_report_en.report_conversion_mmu[LANG].format((CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha, (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha, CLASSTOT['31'] * bxsize_ha, CLASSTOT['32']*bxsize_ha, CLASSTOT['33'] * bxsize_ha, CLASSTOT['10'] * bxsize_ha, (CLASSTOT['41'] + CLASSTOT['42'] + CLASSTOT['43'] + CLASSTOT['44']) *bxsize_ha) +\
#                  roadless_report_en.report_rates_conversion_mmu[LANG].format((CLASSTOT['21'] + CLASSTOT['24']) * bxsize_ha/deltaYY1, (CLASSTOT['22'] + CLASSTOT['23']) * bxsize_ha/deltaYY2, CLASSTOT['31'] * bxsize_ha/deltaYY1, CLASSTOT['32']*bxsize_ha/deltaYY2) +\
#                  roadless_report_en.report_emission_mmu[LANG].format(PXPTOT['Deforest_p1'] * biomass_valuePx, PXPTOT['Deforest_p2'] * biomass_valuePx, PXPTOT['Degrad_p1'] *  biomass_valuePx, PXPTOT['Degrad_p2']* biomass_valuePx) +\
#                  roadless_report_en.report_annual_emission_rates[LANG].format(PXPTOT['Deforest_p1'] * biomass_valuePx / deltaYY1, PXPTOT['Deforest_p2'] * biomass_valuePx / deltaYY2, PXPTOT['Degrad_p1'] * biomass_valuePx/deltaYY1, PXPTOT['Degrad_p2']*biomass_valuePx/deltaYY2) + \
#                  roadless_report_en.report_pixel_table[LANG].format(FTOT, FTOT * sqrps_ha, NFTOT, NFTOT * sqrps_ha,
#                                                                     FNF1TOT, FNF1TOT * sqrps_ha, FNF2TOT,
#                                                                     FNF2TOT * sqrps_ha, NDTOT, NDTOT * sqrps_ha,
#                                                                     FNF1TOT * sqrps_ha / deltaYY1,
#                                                                     FNF2TOT * sqrps_ha / deltaYY2) + \
# \


    return template

# ----------
# main business function
# ----------
def RunDegradation_ROADLESS(progress, thisIface, overwrite, master_img, outFolder, outBasename, kernel_size, biomass_value,
                            biomassDegradPercent, LANG,  startYY1, endYY1, startYY2, endYY2, forest_mmu_fraction,
                            useConversionMapBool, conversionMapFile,
                            useDisagShpBool, disagShp, disagField, useExceptMapBool, exceptMap):


    progress.setValue(1)
    # create a temporary warped filename
    warpedEFMap =os.path.join( tmpdir(), '{}_warped.gtif'.format(outBasename))

    # create a temporary rasterized disagregation layer
    disagMap = os.path.join( tmpdir(), '{}_disag.gtif'.format(outBasename))

    # create a temporary warped exception filename
    warpedExceptMap = os.path.join( tmpdir(), '{}_except.gtif'.format(outBasename))

    outname = os.path.join(outFolder, outBasename.replace('.tif',''))
    print 'A'

    try:


        if useConversionMapBool:
            msg = {'Activity map': master_img, 'MMU size (px)': kernel_size, 'Output name': outname,
                   'Overwrite': overwrite, 'Use conversion map':useConversionMapBool, 'Conversion map file':conversionMapFile}
        else:
            msg = {'Activity map': master_img, 'MMU size (px)': kernel_size, 'Output name': outname,
                   'Overwrite': overwrite, 'Use conversion map': useConversionMapBool, 'Biomass value ':biomass_value,
                   'Degradation emission as percentage of deforestation emission':biomassDegradPercent}
        
        print 'B'
        kernel_size = int(kernel_size)
        print 'B1'
        print biomass_value
        biomass_value = float(biomass_value)
        print 'B2'
        # -------------------------------------------------------------------
        # ------ DEL out files and tmp files if necessary  ------------------
        # -------------------------------------------------------------------
        # rule: if a similar file already existed, try deleting it and files attached to it in principle.
        if overwrite:
            if os.path.exists(outname + '_class.tif'):
                if not deleteFile(outname+'_class.tif'):
                    return False
            if os.path.exists(outname + '_change.tif'):
                if not deleteFile(outname+'_change.tif'):
                    return False
            if os.path.exists(outname + '_biomass.tif'):
                if not deleteFile(outname + '_biomass.tif'):
                    return False
        print 'B3'
        # always delete warped file (in case it was not deleted at the end of the process).
        if os.path.exists(warpedEFMap):
            deleteFile(warpedEFMap+'.aux.xml') # try silently
            if not deleteFile(warpedEFMap):
                return False
        if os.path.exists(warpedExceptMap):
            deleteFile(warpedExceptMap + '.aux.xml')  # try silently
            if not deleteFile(warpedExceptMap):
                return False

        print 'C'
        # ------------------------------------------------------------------
        # ------------------------- OPEN MASTER  ---------------------------
        # ------------------------------------------------------------------
        master_ds = gdal.Open(master_img, gdal.GA_ReadOnly)
        #master_bands=master_ds.RasterCount
        master_cols = master_ds.RasterXSize
        master_rows = master_ds.RasterYSize
        master_imgGeo = master_ds.GetGeoTransform()
        m_ulx = master_imgGeo[0]
        m_uly = master_imgGeo[3]
        m_lrx = master_imgGeo[0] + master_cols * master_imgGeo[1]
        m_lry = master_imgGeo[3] + master_rows * master_imgGeo[5]
        prj = master_ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        projRef = master_ds.GetProjectionRef()
        sqrps_ha = master_imgGeo[1] * master_imgGeo[1] * 1. / 10000.0  # gives the size of a pixel in ha

        #if srs.IsProjected() and srs.GetAttrValue('unit') in ['metre', 'meter', 'metres', 'meters', 'm']: #may not work with some continental projections
        if not srs.GetAttrValue('unit') in ['metre', 'meter', 'metres', 'meters', 'm']:
              return False

        # ----------------------------------------------------
        # -------------        INFO   ------------------------
        # ----------------------------------------------------
        msg={"Activity map Rows":master_rows, "Activity map Columns":master_cols,"Activity map Pixel resolution":master_imgGeo[1],"Activity map unit":srs.GetAttrValue('unit'),"Activity map ULX":m_ulx, "Activity map ULY":m_uly,"Activity map LRX":m_lrx,"Activity map LRY":m_lry,"Activity map no data value":master_ds.GetRasterBand(1).GetNoDataValue()}
        out_cols=int(master_cols/kernel_size)
        out_rows=int(master_rows/kernel_size)

        # ----------------------------------------
        # ---- Warp emission map, if required ----
        # ----------------------------------------
        print 'D ', useConversionMapBool
        if useConversionMapBool:
            warpError=alignToImg(master_img, conversionMapFile, warpedEFMap, 'near')
            if warpError!= 0:
                return False
            wefmFID = gdal.Open(warpedEFMap, gdal.GA_ReadOnly)
            inBFM = wefmFID.GetRasterBand(1).ReadAsArray().astype(numpy.float)
        # ----------------------------------------
        # ---- Warp exception map, if required ----
        # ----------------------------------------
        uniqExceptCount = ''
        print 'useExceptMapBool ', useExceptMapBool
        if useExceptMapBool:
            warpError = alignToImg(master_img, exceptMap[0], warpedExceptMap, 'near')
            if warpError != 0:
                return False
            exceptFID = gdal.Open(warpedExceptMap, gdal.GA_ReadOnly)
            inExcept = exceptFID.GetRasterBand(1).ReadAsArray().astype(numpy.int)
            # get unique values
            uniqExceptCount = uniqValCountRaster(warpedExceptMap, sqrps_ha)
            
        print 'E'
        # ------------------------------------
        # rasterize disaggregation layer if required
        # ------------------------------------
        if useDisagShpBool:
            # reproject shp if necessary
            try:
                disagElements = rasterizeDisag(disagShp[0], disagField, master_img, kernel_size, disagMap)
                if disagElements == False:
                    return False
                disagMapFID = gdal.Open(disagMap, gdal.GA_ReadOnly)
                disagArray = disagMapFID.GetRasterBand(1).ReadAsArray(0, 0, disagMapFID.RasterXSize, disagMapFID.RasterYSize)
                disaMapFid = None
                # now create the disaggregated associative arrays
                EMDegP1Disag = {}
                EMDegP2Disag = {}
                EMDefP1Disag = {}
                EMDefP2Disag = {}
                ARDegP1Disag = {}
                ARDegP2Disag = {}
                ARDefP1Disag = {}
                ARDefP2Disag = {}
                for ii in disagElements:
                    EMDegP1Disag[disagElements[ii]] = 0 # Emission, Degradation, Period 1, disaggregated
                    EMDegP2Disag[disagElements[ii]] = 0
                    EMDefP1Disag[disagElements[ii]] = 0
                    EMDefP2Disag[disagElements[ii]] = 0
                    ARDegP1Disag[disagElements[ii]] = 0 # Areas, Degradation, Period 1, disaggregated
                    ARDegP2Disag[disagElements[ii]] = 0
                    ARDefP1Disag[disagElements[ii]] = 0
                    ARDefP2Disag[disagElements[ii]] = 0
            except Exception, e:
                return False
        print 'F'
        # ------------------------------------
        # Processing: loop reading master_img [and warpedEFMap if needed] by kernels size
        # computation done for each chunk of data
        # ------------------------------------
        #nodata = (master_ds.GetRasterBand(1).GetNoDataValue())

        IN = master_ds.GetRasterBand(1).ReadAsArray().astype(numpy.byte)
        print 'f1'
        OUT_CLASS = numpy.zeros( (out_rows, out_cols))
        print 'f11'
        OUT_ND = numpy.zeros( (out_rows, out_cols) ) #IN*0
        print 'f12'
        OUT_FF = numpy.zeros( (out_rows, out_cols) ) #IN*0
        OUT_NFNF = numpy.zeros( (out_rows, out_cols) ) #IN*0
        OUT_FNF1 = numpy.zeros( (out_rows, out_cols) ) #IN*0
        OUT_FNF2 = numpy.zeros( (out_rows, out_cols) ) #IN*0
        print 'f1x'
        forestThreshold = forest_mmu_fraction / 100.0
        print 'F2'
        inGT = master_ds.GetGeoTransform()
        outGT = (inGT[0], inGT[1] * kernel_size, inGT[2], inGT[3], inGT[4], inGT[5]*kernel_size )
        print 'outGT ',outGT

        OUT_EMP1 = numpy.zeros((out_rows, out_cols))
        OUT_EMP2 = numpy.zeros((out_rows, out_cols))
        print 'F22 ',outGT
        EMDefP1TOT = 0
        EMDefP2TOT = 0
        EMDegP1TOT = 0
        EMDegP2TOT = 0
        #exceptTOT  = 0

        CLASSTOT = {'0':0, '99':0, '10':0, '21':0, '22':0,'23':0, '24':0, '31':0, '32':0, '33':0, '41':0, '42':0, '43':0, '44':0}
        PXPTOT = {'Degrad_p1':0, 'Degrad_p2':0, 'Deforest_p1':0, 'Deforest_p2':0, 'FF_10':0, 'FF_4x':0, 'FF_2x':0 , 'FF_3x':0, 'NF_10':0, 'NF_2x':0, 'NF_3x':0, 'NF_4x':0, 'FNF1_4x':0, 'FNF2_4x':0, 'ND_1x':0, 'ND_2x':0, 'ND_3x':0, 'ND_4x':0, 'ND_0x':0}
        FTOT, NFTOT, FNF1TOT, FNF2TOT, NDTOT = [0,0,0,0,0]

        print 'G', outGT
        try :
            lastProgress = datetime.now()
            c, r = 0,0
            thisC, thisR = 0,0
            while c+kernel_size <= master_cols:
                thisProgress = datetime.now()
                timeDiff = thisProgress - lastProgress
                if  timeDiff.seconds> 2:
                    progress.setValue(int(100*c/master_rows))
                    lastProgress = thisProgress
                #print c, master_cols
                #tmp = master_ds.GetRasterBand(1).ReadAsArray(0, r, kernel_size, out_rows*kernel_size).astype(numpy.byte)
                #inBFMTMP = wefmFID.GetRasterBand(1).ReadAsArray(0, r, kernel_size, out_rows*kernel_size).astype(numpy.float)
                while r+kernel_size <= master_rows:
                    #masked = tmp[r:r+kernel_size, :]exceptMap
                    masked = IN[r:r+kernel_size,c:c+kernel_size]
                    if useExceptMapBool:
                        # set to 0 any data for which an exception code was found
                        masked *= ( inExcept[r:r+kernel_size,c:c+kernel_size] == 0).astype(numpy.int)
                    #inBFM = inBFMTMP[r:r+kernel_size, :]

                    FF = numpy.count_nonzero(masked == 1)
                    NF = numpy.count_nonzero(masked == 2)
                    FNF1 = numpy.count_nonzero(masked == 3)
                    FNF2 = numpy.count_nonzero(masked == 4)
                    ND = numpy.count_nonzero(masked <1) + numpy.count_nonzero(masked > 4) #set to no data anything that is not 1,2,3,4. For example, gdalwarp set default to 128
                    TOT = FF + NF + FNF1 + FNF2   # count of pixels different from ND
                    F0 = FF + FNF1 + FNF2
                    third = int(round(TOT * forestThreshold))
                    FTOT += FF
                    NFTOT += NF
                    FNF1TOT += FNF1
                    FNF2TOT += FNF2
                    NDTOT += ND
                    EMDefP1 = 0 # Emission Deforestation Period 1 (historical)
                    EMDefP2 = 0 # Emission Deforestation Period 2 (recent)
                    EMDegP1 = 0 # Emission Degradation Period 1 (historical)
                    EMDegP2 = 0 # Emission Degradation Period 2 (recent)

                    # ---- Decision tree ---
                    if ND > TOT / 3.0:
                        UNIT_CLASS = 0
                        PXPTOT['ND_0x'] += FF + NF + FNF1 + FNF2 + ND
                    else: # ND < NPIXEL / 3.0
                        if F0 < third:
                            if FNF1 == 0 and FNF2 == 0:
                                UNIT_CLASS = 41
                                PXPTOT['FF_4x'] += FF
                                PXPTOT['NF_4x'] += NF
                                PXPTOT['ND_4x'] += ND
                            elif FNF1 != 0 and FNF2 == 0:
                                UNIT_CLASS = 42
                                PXPTOT['FF_4x'] += FF
                                PXPTOT['NF_4x'] += NF
                                PXPTOT['FNF1_4x'] += FNF1
                                PXPTOT['ND_4x'] += ND
                            elif FNF1 == 0 and FNF2 != 0:
                                UNIT_CLASS = 43
                                PXPTOT['FF_4x'] += FF
                                PXPTOT['NF_4x'] += NF
                                PXPTOT['FNF2_4x'] += FNF2
                                PXPTOT['ND_4x'] += ND
                            elif FNF1 != 0 and FNF2 != 0:
                                UNIT_CLASS = 44
                                PXPTOT['FF_4x'] += FF
                                PXPTOT['NF_4x'] += NF
                                PXPTOT['FNF1_4x'] += FNF1
                                PXPTOT['FNF2_4x'] += FNF2
                                PXPTOT['ND_4x'] += ND
                            else: UNIT_CLASS = 99 # to debug the logic, closes the cases
                        else: # F0>= 30%
                            if FNF1 == 0 and FNF2 == 0:
                                UNIT_CLASS = 10
                                PXPTOT['FF_10'] += FF
                                PXPTOT['NF_10'] += NF
                                PXPTOT['ND_1x'] += ND
                            elif FNF1 !=0 and FNF2 == 0:

                                if FF > third:
                                    # degradation, period 1 (historical)
                                    UNIT_CLASS = 31
                                    PXPTOT['Degrad_p1'] += FNF1
                                    PXPTOT['NF_3x'] += NF
                                    PXPTOT['FF_3x'] += FF
                                    PXPTOT['ND_3x'] += ND

                                    if useConversionMapBool:
                                        EMDegP1 = numpy.sum( (masked == 3).astype(int) * inBFM[r:r + kernel_size, c:c + kernel_size]) * sqrps_ha * biomassDegradPercent / 100.0
                                        if useDisagShpBool:
                                            EMDegP1Disag[ disagElements[disagArray[r/kernel_size,c/kernel_size]] ] += EMDegP1
                                            ARDegP1Disag[ disagElements[disagArray[r/kernel_size,c/kernel_size]] ] += numpy.sum( (masked == 3) ).astype(int) * sqrps_ha
                                    elif useDisagShpBool:
                                        EMDegP1Disag[ disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha * biomass_value * biomassDegradPercent / 100.0
                                        ARDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha
                                else:
                                    # Deforestation, period 1 (historical)
                                    UNIT_CLASS = 21
                                    PXPTOT['Deforest_p1'] += FNF1
                                    PXPTOT['NF_2x'] += NF
                                    PXPTOT['FF_2x'] += FF
                                    PXPTOT['ND_2x'] += ND

                                    if useConversionMapBool:
                                        EMDefP1 = numpy.sum( (masked == 3).astype(int) * inBFM[r:r + kernel_size, c:c + kernel_size]) * sqrps_ha
                                        if useDisagShpBool:
                                            EMDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDefP1
                                            ARDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += numpy.sum( (masked == 3)).astype(int) * sqrps_ha
                                    elif useDisagShpBool:
                                        EMDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1  * sqrps_ha * biomass_value
                                        ARDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1  * sqrps_ha
                            elif FNF1 == 0 and FNF2 != 0:
                                if FF > third:
                                    # degradation, degradation, period 2 (recent)
                                    UNIT_CLASS = 32
                                    PXPTOT['Degrad_p2'] += FNF2
                                    PXPTOT['NF_3x'] += NF
                                    PXPTOT['FF_3x'] += FF
                                    PXPTOT['ND_3x'] += ND

                                    if useConversionMapBool:
                                        EMDegP2 = numpy.sum( (masked == 4).astype(int) * inBFM[r:r + kernel_size, c:c + kernel_size]) * sqrps_ha* biomassDegradPercent / 100.0
                                        if useDisagShpBool:
                                            EMDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDegP2
                                            ARDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += numpy.sum( (masked == 4)).astype(int) * sqrps_ha
                                    elif useDisagShpBool:
                                        EMDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha * biomass_value * biomassDegradPercent / 100.0
                                        ARDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha
                                else:
                                    # deforestation, period 2 (recent)
                                    UNIT_CLASS = 22
                                    PXPTOT['Deforest_p2'] += FNF2
                                    PXPTOT['NF_2x'] += NF
                                    PXPTOT['FF_2x'] += FF
                                    PXPTOT['ND_2x'] += ND

                                    if useConversionMapBool:
                                        EMDefP2 = numpy.sum((masked == 4).astype(int) * (inBFM[r:r + kernel_size, c:c + kernel_size])) * sqrps_ha
                                        if useDisagShpBool:
                                            EMDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDefP2
                                            ARDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += numpy.sum((masked == 4)).astype(int) * sqrps_ha
                                    elif useDisagShpBool:
                                        EMDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha * biomass_value
                                        ARDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha
                            elif FNF1 !=0 and FNF2 != 0:
                                if FF > third:
                                    # degradation, period 1 and 2
                                    UNIT_CLASS = 33
                                    PXPTOT['Degrad_p1'] += FNF1
                                    PXPTOT['Degrad_p2'] += FNF2
                                    PXPTOT['NF_3x'] += NF
                                    PXPTOT['FF_3x'] += FF
                                    PXPTOT['ND_3x'] += ND

                                    if useConversionMapBool:
                                        EMDegP1 = numpy.sum( (masked == 3).astype(int) * (inBFM[r:r + kernel_size, c:c + kernel_size])) * sqrps_ha * biomassDegradPercent / 100.0
                                        EMDegP2 = numpy.sum((masked == 4).astype(int) * (inBFM[r:r + kernel_size, c:c + kernel_size])) * sqrps_ha * biomassDegradPercent / 100.0
                                        if useDisagShpBool:
                                            EMDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDegP1
                                            EMDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDegP2
                                            ARDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += numpy.sum( (masked == 3)).astype(int) * sqrps_ha
                                            ARDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += numpy.sum((masked == 4)).astype(int) * sqrps_ha
                                    elif useDisagShpBool:
                                        EMDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha * biomass_value * biomassDegradPercent / 100.0
                                        EMDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha * biomass_value * biomassDegradPercent / 100.0
                                        ARDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha
                                        ARDegP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha
                                elif (FF+FNF2) > third:
                                    # deforestation period 2 and degradation period 1
                                    UNIT_CLASS = 23
                                    PXPTOT['Deforest_p2'] += FNF2
                                    PXPTOT['Degrad_p1'] += FNF1
                                    PXPTOT['NF_2x'] += NF
                                    PXPTOT['FF_2x'] += FF
                                    PXPTOT['ND_2x'] += ND

                                    if useConversionMapBool:
                                        EMDegP1 = numpy.sum((masked == 3).astype(int) * (inBFM[r:r + kernel_size, c:c + kernel_size])) * sqrps_ha * biomassDegradPercent / 100.0
                                        EMDefP2 = numpy.sum((masked == 4).astype(int) * (inBFM[r:r + kernel_size, c:c + kernel_size])) * sqrps_ha
                                        if useDisagShpBool:
                                            EMDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDegP1
                                            EMDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDefP2
                                            ARDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] +=  numpy.sum((masked == 3)).astype(int) * sqrps_ha
                                            ARDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += numpy.sum((masked == 4)).astype(int) * sqrps_ha
                                    elif useDisagShpBool:
                                        EMDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha * biomass_value
                                        EMDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha * biomass_value * biomassDegradPercent / 100.0
                                        ARDefP2Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF2 * sqrps_ha
                                        ARDegP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha
                                else:
                                    # deforestation period 1 and change in period 2
                                    UNIT_CLASS = 24
                                    PXPTOT['Deforest_p1'] += FNF1
                                    PXPTOT['NF_2x'] += FNF2
                                    PXPTOT['NF_2x'] += NF
                                    PXPTOT['FF_2x'] += FF
                                    PXPTOT['ND_2x'] += ND

                                    if useConversionMapBool:
                                        EMDefP1 = numpy.sum((masked == 3).astype(int) * (inBFM[r:r + kernel_size, c:c + kernel_size])) * sqrps_ha
                                        if useDisagShpBool:
                                            EMDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += EMDefP1
                                            ARDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += numpy.sum((masked == 3)).astype(int) * sqrps_ha
                                    elif useDisagShpBool:
                                        EMDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha * biomass_value
                                        ARDefP1Disag[disagElements[disagArray[r / kernel_size, c / kernel_size]]] += FNF1 * sqrps_ha

                            else: UNIT_CLASS = 99

                    CLASSTOT[str(UNIT_CLASS)] += 1

                    if useConversionMapBool:
                        EMDefP1TOT += EMDefP1
                        EMDefP2TOT += EMDefP2
                        EMDegP1TOT += EMDegP1
                        EMDegP2TOT += EMDegP2

                    #OUT_ND[r:r+kernel_size,c:c+kernel_size] = ND
                    OUT_ND[thisR, thisC] = ND
                    #OUT_FF[r:r+kernel_size,c:c+kernel_size] = FF
                    OUT_FF[thisR, thisC] = FF
                    #OUT_NFNF[r:r+kernel_size,c:c+kernel_size] = NF
                    OUT_NFNF[thisR, thisC] = NF
                    #OUT_FNF1[r:r+kernel_size,c:c+kernel_size] = FNF1
                    OUT_FNF1[thisR, thisC] = FNF1
                    #OUT_FNF2[r:r+kernel_size,c:c+kernel_size] = FNF2
                    OUT_FNF2[thisR, thisC] = FNF2
                    #IN[r:r+kernel_size,c:c+kernel_size]=UNIT_CLASS
                    OUT_CLASS[thisR, thisC] = UNIT_CLASS
                    if useConversionMapBool:
                        OUT_EMP1[thisR, thisC] = EMDefP1 + EMDegP1
                        OUT_EMP2[thisR, thisC] = EMDefP2 + EMDegP2

                    r += kernel_size
                    thisR +=1
                r = 0
                thisR = 0
                c += kernel_size
                thisC += 1

        except Exception, e:
            print 'crash'
            master_ds = None
            if useConversionMapBool:
                wefmFID = None
            return False

        # clean up temporary files
        print 'H', outGT
        if useConversionMapBool:
            wefmFID = None  # free FID before deleting
        if os.path.exists(warpedEFMap):
            deleteFile(warpedEFMap+'aux.xml') # try silently
            if (not deleteFile(warpedEFMap)):
                return False

        # --------------------------------------------------------------------------
        # save  UNIT_CLASS
        # --------------------------------------------------------------------------
        try:
            print 'I'
            driver = gdal.GetDriverByName("GTiff")
            dst_ds = driver.Create( outname+'_class.tif', out_cols, out_rows,1, gdal.GDT_Byte, options = [ 'COMPRESS=LZW','BIGTIFF=IF_SAFER' ]) #GDT_Byte
            print dst_ds
            print 'I1'
            print outGT
            print 'I2'
            dst_ds.SetGeoTransform( outGT )
            print master_ds.GetProjectionRef() 
            dst_ds.SetProjection( master_ds.GetProjectionRef() )
            #dst_ds.SetMetadata({'Impact_product_type': 'MMU class', 'Impact_operation':"MMU degradation", 'Impact_version':IMPACT.get_version(), 'Impact_band_interpretation':'1:Classification'})
            dst_ds.GetRasterBand(1).SetNoDataValue(0)
            outband = dst_ds.GetRasterBand(1)
            print 'I2'
            outband.WriteArray(OUT_CLASS)
            print 'I3'
            # ADD PALETTE
            dst_ds.GetRasterBand(1).SetRasterColorInterpretation(gdal.GCI_PaletteIndex)
            c = gdal.ColorTable()
            ctable = [[0,  (192, 192, 192)],
                      [99, (0, 0, 0)],
                      [10, (121,163,121)],
                      [21, (105,30,248)],
                      [22, (255,69,0)],
                      [23, (163,67,32)],
                      [24, (105,30,248)],
                      [31, (115,255,0)],
                      [32, (248,185,24)],
                      [33, (63,221,224)],
                      [41, (228,230,194)],
                      [42, (228,230,194)],
                      [43, (228,230,194)],
                      [44, (228, 230, 194)]]
            for cid in range(0, len(ctable)):
                c.SetColorEntry(ctable[cid][0], ctable[cid][1])
            dst_ds.GetRasterBand(1).SetColorTable(c)
            dst_ds.FlushCache()
            dst_ds = None
            OUT_CLASS = None

            thisIface.addRasterLayer(outname+'_class.tif', '{} classes'.format(outBasename))
        except Exception, e:
            return False

        # --------------------------------------------------------------------------
        # save  CHANGE
        # --------------------------------------------------------------------------
        try:
            print 'H2'
            driver = gdal.GetDriverByName("GTiff")
            dst_ds = driver.Create( outname+'_change.tif', out_cols, out_rows, 5, gdal.GDT_UInt16, options = [ 'COMPRESS=LZW','BIGTIFF=IF_SAFER' ]) #GDT_Byte
            dst_ds.SetGeoTransform( outGT )
            dst_ds.SetProjection( master_ds.GetProjectionRef())
            #dst_ds.SetMetadata({'Impact_product_type': 'MMU change','Impact_operation':"degradation",'Impact_band_interpretation':'1:ND, 2:FF, 3:NFNF, 4:FNF1, 5:FNF2', 'Impact_default_bands':'4,1,5','Impact_version':IMPACT.get_version()})
            dst_ds.GetRasterBand(1).WriteArray(OUT_ND)
            dst_ds.GetRasterBand(2).WriteArray(OUT_FF)
            dst_ds.GetRasterBand(3).WriteArray(OUT_NFNF)
            dst_ds.GetRasterBand(4).WriteArray(OUT_FNF1)
            dst_ds.GetRasterBand(5).WriteArray(OUT_FNF2)
        except Exception,e:
            return False

        dst_ds.FlushCache()
        dst_ds = None
        OUT_ND = None
        OUT_FF = None
        OUT_NFNF = None

        print 'H23'
        thisIface.addRasterLayer(outname+'_change.tif', '{} change'.format(outBasename) )

        # --------------------------------------------------------------------------
        # save  BIOMASS
        # --------------------------------------------------------------------------
        try:
            print 'J1'
            driver = gdal.GetDriverByName("GTiff")
            dst_ds = driver.Create( outname+'_biomass.tif', out_cols, out_rows,3, gdal.GDT_Float32, options = [ 'COMPRESS=LZW','BIGTIFF=IF_SAFER' ])
            dst_ds.SetGeoTransform( outGT )
            dst_ds.SetProjection( master_ds.GetProjectionRef())
            if useConversionMapBool:
                #dst_ds.SetMetadata({'Impact_product_type': 'MMU biomass', 'Impact_operation': "degradation",
                #                    'Impact_band_interpretation': '1:FNF1*biomass_factor_map, 2:FNF2*biomass_factor_map, 3:(FNF1+FNF2)*biomass_factor_map'})
                dst_ds.GetRasterBand(1).WriteArray(OUT_EMP1)
                dst_ds.GetRasterBand(2).WriteArray(OUT_EMP2)
                dst_ds.GetRasterBand(3).WriteArray( OUT_EMP1 + OUT_EMP2 )
            else:
                dst_ds.SetMetadata({'Impact_product_type': 'MMU biomass','Impact_operation':"degradation", 'Impact_band_interpretation':'1:FNF1*biomass_factor, 2:FNF2*biomass_factor, 3:(FNF1+FNF2)*biomass_factor'})
                dst_ds.GetRasterBand(1).WriteArray(OUT_FNF1 * biomass_value)
                dst_ds.GetRasterBand(2).WriteArray(OUT_FNF2 * biomass_value)
                dst_ds.GetRasterBand(3).WriteArray((OUT_FNF1 + OUT_FNF2)*biomass_value)
            if useDisagShpBool:
                pass
            dst_ds.FlushCache()
        except Exception,e:
            return False

        dst_ds = None
        OUT_FNF1 = None
        OUT_FNF2 = None
        master_ds = None
        print 'J2'
        thisIface.addRasterLayer(outname+'_biomass.tif', '{} biomass'.format(outBasename))

        try:
            UL_LL = toLonLat(m_ulx, m_uly, projRef )
            LR_LL = toLonLat(m_lrx, m_lry, projRef )
            if useDisagShpBool:
                EMDisag = {'useDisagShpBool':useDisagShpBool,'disagElements':disagElements,
                       'EmDegP1':EMDegP1Disag,'EmDegP2':EMDegP2Disag,
                       'EmDefP1':EMDefP1Disag, 'EmDefP2':EMDefP2Disag,
                       'ArDegP1':ARDegP1Disag,'ArDegP2':ARDegP2Disag,
                       'ArDefP1':ARDefP1Disag,'ArDefP2':ARDefP2Disag
                       }
            else: EMDisag={'useDisagShpBool':False}
            # report for exceptions
            if useExceptMapBool:
                for ii in uniqExceptCount:
                    pass

            report = getTemplate(useConversionMapBool, master_img, conversionMapFile, LANG, FTOT, NFTOT, FNF1TOT, FNF2TOT, NDTOT, PXPTOT,
                                 EMDefP1TOT, EMDefP2TOT, EMDegP1TOT, EMDegP2TOT, EMDisag, useExceptMapBool, uniqExceptCount,
                                 master_imgGeo[1], startYY1, endYY1, startYY2, endYY2, CLASSTOT, kernel_size,
                                 biomass_value, biomassDegradPercent, forestThreshold, UL_LL[0], UL_LL[1], LR_LL[0], LR_LL[1])

            text_file = open(outname + "_report_" + LANG + '.html', "w")
            text_file.write(report)
            text_file.close()
        except Exception, e:
            pass

    except Exception,e:

        dst_ds = None
        if os.path.exists(outname):
            os.remove(outname)
        if os.path.exists(outname+'.aux.xml'):
            os.remove(outname+'.aux.xml')
        if os.path.exists(outname+"_tmp"):
            os.remove(outname+"_tmp")
        if os.path.exists(outname+'_tmp.aux.xml'):
            os.remove(outname+'_tmp.aux.xml')

        return False
