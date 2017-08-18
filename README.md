# carborama
QGIS plugin to compute carbon emission from deforestation and forest degradation.

This plugin was designed for the need of the iForce team, JRC, European Commission.
Its purpose is to allow computing forest carbon emission, on the basis of maps of detection of deforestation and forest degradation.
The plugin allows using either a constant biomass factor, or a map of carbon emissions (in t/C/ha). It can also use a disaggregation shapefile, to sort out areas of forest degradation and deforestation by classes of landcover. Optionnally, it can also use a map of pixels exception, where any pixel flagged with a non-0 value is taken out of the total areas counting.
