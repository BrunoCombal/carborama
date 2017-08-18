# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Carborama
                                 A QGIS plugin
 Compute Forest CO2 equivalent emissions, due to degradation and deforestation
                              -------------------
        begin                : 2017-08-09
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Bruno Combal
        email                : bruno.combal@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4 import QtCore
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QComboBox, QListWidget, QMessageBox, QProgressBar
from qgis.core import QgsMapLayerRegistry, QgsMapLayer
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from carborama_dialog import CarboramaDialog
import os.path
import doMMUCounting
from os.path import expanduser
import string


class Carborama:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Carborama_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Carborama')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Carborama')
        self.toolbar.setObjectName(u'Carborama')


        self.UIParams={"overwrite":True, 
                        "master_img":None,
                        "outBasename":None,
                        "outFolder":None,
                        "kernel_size":3,
                        "biomass_value":None,
                        "biomassDegradPercent":None,
                        "language":'EN',
                        "startYY1":None, "endYY1":None, "startYY2":None, "endYY2":None,
                        "forest_mmu_fraction":None,
                        "useConversionMapBool":False, "conversionMap":None,
                        "useDisagShpBool":None, "disagShp":None, "disagField":None,
                        "useExceptMap":False, "exceptMap":None}

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Carborama', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = CarboramaDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Carborama/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Carborama'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Carborama'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def displayTextLine(self, key, text):
        if key == 'lineActivityMap':
            self.dlg.lineActivityMap.setText(text)
        if key == 'lineConversionMap':
            self.dlg.lineConversionMap.setText(text)
            if self.dlg.radioEmissionConstant.isChecked():
                self.dlg.radioEmissionConstant.setChecked(False)
                self.dlg.radioEmissionMap.setChecked(True)
        if key == 'lineDisagShp':
            self.dlg.lineDisagShp.setText(text)
            self.UIParams['disagShp'] = True
        if key == 'lineExceptShp':
            self.dlg.lineExceptShp.setText(text)
            self.UIParams['exceptMap'] = True
        if key == 'lineOutputFolder':
            self.dlg.lineOutputFolder.setText(text)

    def getFileFromDisk(self, key, displayKey):
        dialog = QFileDialog()
        fname = dialog.getOpenFileName(self.dlg, self.tr("Choose a raster file"))
        # test validity?
        self.UIParams[key] = fname
        self.displayTextLine(displayKey, fname)

    def getFolder(self, key):
        dialog = QFileDialog()
        if self.UIParams[key] is None:
            self.UIParams[key] = str(dialog.getExistingDirectory(self.dlg, "Select Directory", expanduser("~"), dialog.ShowDirsOnly))
        elif  os.path.isdir(self.UIParams[key]):
            self.UIParams[key] = str(dialog.getExistingDirectory(self.dlg, "Select Directory", self.UIParams[key], dialog.ShowDirsOnly))
        else:
            self.UIParams[key] = str(dialog.getExistingDirectory(self.dlg, "Select Directory", expanduser("~"), dialog.ShowDirsOnly))

        if self.UIParams[key] is not None:
            self.displayTextLine('lineOutputFolder', self.UIParams[key])

    def onChangedSpinboxEmission(self):
        # if the spinBox is touched, set the radio button on
        if self.dlg.radioEmissionMap.isChecked():
                self.dlg.radioEmissionConstant.setChecked(True)
                self.dlg.radioEmissionMap.setChecked(False)
        # and collect the data
        self.UIParams['biomass_value'] = self.dlg.spinBoxEmissionConstant.value()

    def onChangedSpinbox(self, key, value):
        self.UIParams[key] = value

    def getRasterFromRegistry(self, key, displayKey, type='raster'):
        layers =  QgsMapLayerRegistry.instance().mapLayers().values()
        listDialog = QListWidget()
        correspondance = {}
        for layer in layers:
            if layer.type() == QgsMapLayer.RasterLayer:
                listDialog.addItem( layer.name())
                print layer.name()

        listDialog.show()

    def getTextValue(self, key, value):
        self.UIParams[key] = value.strip()

    def getYear(self, key, value):
        self.UIParams[key] = value

    def regularizeParams(self):
        if self.UIParams['outBasename'] == '':
            self.UIParams['outBasename'] = None

    def checkFiles(self):
        # do input file actually exist?
        msg = ''
        checkOk = True
        if self.UIParams['master_img'] is not None:
            if not os.path.exists(self.UIParams['master_img']):
                msg += 'Activity map {} not found\n'.format(self.UIParams['master_img'])
                checkOk = False
                self.UIParams['master_img'] = None
                self.dlg.lineActivityMap.setText('')
        
        if self.UIParams['conversionMap'] is not None:
            if not os.path.exists(self.UIParams['conversionMap']):
                if self.UIParams['useConversionMapBool']:
                    msg += 'Conversion map file {} not found\n'.format(self.UIParams['conversionMap'])
                    checkOk = False
                    self.UIParams['conversionMap'] = None

        if self.UIParams['disagShp'] is not None:
            if not os.path.exists(self.UIParams['disagShp']):
                if self.UIParams['useDisagShpBool']:
                    msg += 'Disaggregation shapefile {} not found\n'.format(self.UIParams['disagShp'])
                    checkOk = False
                    self.UIParams['disagShp'] = None

        if self.UIParams['exceptMap'] is not None:
            if not os.path.exists(self.UIParams['exceptMap']):
                if self.UIParams['useExceptMap']:
                    msg += 'Exception map file {} not found\n'.format(self.UIParams['exceptMap'])
                    checkOk = False
                    self.UIParams['exceptMap'] = None

        return (checkOk, msg)

    def OkToRun(self):
        # force chekFiles
        oktorun = True
        msg = ''
        returnCheck = self.checkFiles()

        if returnCheck[0] == False:
            self.alert(returnCheck[1])
            return False

        # if files are defined, they are on disk
        if self.UIParams['master_img'] is None:
            msg += 'Activity map must be defined and exist on the disk\n'
            oktorun = False
        if self.UIParams['conversionMap'] is None and self.UIParams['useConversionMapBool'] == True:
            msg += 'Biomass conversion map must be defined and exist on disk\n'
            oktorun = False
        if self.UIParams['disagShp'] is None and self.UIParams['useDisagShpBool'] == True:
            msg += 'Disaggregation shapefile must be defined and exist on disk\n'
            oktorun = False
        if self.UIParams['exceptMap'] is None and self.UIParams['useExceptMap'] == True:
            msg += 'Exception map must be defined and exist on disk\n'
            print self.UIParams['exceptMap'], self.UIParams['useExceptMap']
            oktorun = False
        if self.UIParams['outBasename'] is None:
            msg += 'Please define a basename for the outputs\n'
            oktorun = False
        elif self.UIParams['outBasename'].strip() == '':
            msg += 'Please define a basename for the outputs\n'
            oktorun = False

        if self.UIParams['endYY1'] < self.UIParams['startYY1']:
            msg += 'Period 1 ending year must be greater or equal to the starting year\n'
            print self.UIParams['startYY1'], self.UIParams['endYY1']
            oktorun = False
        if self.UIParams['endYY2'] < self.UIParams['startYY2']:
            msg += 'Period 2 ending year must be greater or equal to the starting year\n'
            oktorun = False
        if self.UIParams['startYY2'] <= self.UIParams['endYY1']:
            msg += 'Start of period 2 must be greater than end of period 1\n'
            oktorun = False

        if oktorun == False:
            msg += 'Please check input parameters\n'
        return (oktorun, msg)


    def doInitGui(self):

        # read default values
        self.UIParams['biomass_value'] = self.dlg.spinBoxEmissionConstant.value()
        self.UIParams['startYY1'] = self.dlg.sbStartYY1.value()
        self.UIParams['endYY1'] = self.dlg.sbEndYY1.value()
        self.UIParams['startYY2'] = self.dlg.sbStartYY2.value()
        self.UIParams['endYY2'] = self.dlg.sbEndYY2.value()
        self.UIParams['biomassDegradPercent'] = self.dlg.spEmissionFraction.value()
        if self.dlg.radioEmissionConstant.isChecked():
            self.UIParams['useConversionMapBool'] = False
        else:
            self.UIParams['useConversionMapBool'] = True
        self.UIParams['biomassDegradPercent'] = self.dlg.spEmissionFraction.value()
        if self.dlg.rbOverwriteNo.isChecked():
            self.UIParams['overwrite'] = True
        else:
            self.UIParams['overwrite'] = False
        if self.dlg.lineDisagShp.text == '':
            self.UIParams['useDisagShpBool'] = False
        else:
            self.UIParams['useDisagShpBoll'] = True
        if self.dlg.lineExceptShp.text() == '':
            self.UIParams['useExceptMap'] = False
        else:
            self.UIParams['useExceptMap'] = True

        self.UIParams['kernel_size'] = self.dlg.sbMMUPixel.value()
        self.UIParams['forest_mmu_fraction'] = self.dlg.sbTreeFraction.value()


        # connect buttons
        self.dlg.buttonActivityMapDisk.clicked.connect(lambda: self.getFileFromDisk('master_img','lineActivityMap'))
        self.dlg.buttonActivityMapRegistry.clicked.connect(lambda: self.getFileFromRegistry('master_img','lineActivityMap'))

        self.dlg.buttonEmissionMapDisk.clicked.connect(lambda: self.getFileFromDisk('conversionMap','lineConversionMap'))
        self.dlg.spinBoxEmissionConstant.valueChanged.connect(self.onChangedSpinboxEmission)

        self.dlg.buttonDisagShpDisk.clicked.connect(lambda: self.getFileFromDisk('disagShp','lineDisagShp'))

        self.dlg.buttonExceptShpDisk.clicked.connect(lambda: self.getFileFromDisk('exceptMap', 'lineExceptShp'))

        self.dlg.sbStartYY1.valueChanged.connect(lambda: self.getYear('startYY1', self.dlg.sbStartYY1.value()) )
        self.dlg.sbEndYY1.valueChanged.connect(lambda: self.getYear('endYY1', self.dlg.sbEndYY1.value()) )
        self.dlg.sbStartYY2.valueChanged.connect(lambda: self.getYear('startYY2', self.dlg.sbStartYY2.value()) )
        self.dlg.sbEndYY2.valueChanged.connect(lambda: self.getYear('endYY2', self.dlg.sbEndYY2.value()) )

        self.dlg.sbMMUPixel.valueChanged.connect(lambda: self.onChangedSpinBox('kernel_size', self.dlg.sbMMUPixel.value()) )
        self.dlg.sbTreeFraction.valueChanged.connect(lambda: self.onChangedSpinbox('forest_mmu_fraction', self.dlg.sbTreeFraction.value()) )

        self.dlg.lineBasename.textChanged.connect(lambda: self.getTextValue('outBasename', self.dlg.lineBasename.text() ) )
        self.dlg.buttonOutputFolder.clicked.connect(lambda: self.getFolder('outFolder'))
        self.dlg.lineOutputFolder.textChanged.connect(lambda: self.getTextValue('outFolder', self.dlg.lineOutputFolder.text()) )

    def alert(self, message):
        thisMessage = QMessageBox()
        thisMessage.setWindowTitle('Critical')
        thisMessage.setIcon(QMessageBox.Critical)
        #thisMessage.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        thisMessage.setStandardButtons(QMessageBox.Ok)
        thisMessage.setText(message)
        result = thisMessage.exec_()

    def run(self):
        """Run method that performs all the real work"""
        self.doInitGui()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        # thisMessage = QMessageBox()
        # thisMessage.setIcon(QMessageBox.Information)
        # msgText = ''
        # for ikey in self.UIParams:
        #     msgText += '{}: {}\n'.format(ikey, self.UIParams[ikey])
        # thisMessage.setText(msgText)
        # thisMessage.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        result = self.dlg.exec_()
        #msgRet = thisMessage.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            oktorun, msgoktorun = self.OkToRun()
            if oktorun:
                for ii in self.UIParams:
                    print ii,' ', self.UIParams[ii]
                progressMessageBar = self.iface.messageBar().createMessage("Computing carbon emmissions")
                progress = QProgressBar()
                progress.setMaximum(100)
                progress.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
                progressMessageBar.layout().addWidget(progress)
                self.iface.messageBar().pushWidget(progressMessageBar, self.iface.messageBar().INFO)
                doMMUCounting.RunDegradation_ROADLESS(progress, self.iface,
                    self.UIParams['overwrite'],
                    self.UIParams['master_img'],
                    self.UIParams['outFolder'], self.UIParams['outBasename'], 
                    self.UIParams['kernel_size'],
                    self.UIParams['biomass_value'], self.UIParams['biomassDegradPercent'],
                    self.UIParams['language'], 
                    self.UIParams['startYY1'], self.UIParams['endYY1'], self.UIParams['startYY2'], self.UIParams['endYY2'], 
                    self.UIParams['forest_mmu_fraction'],
                    self.UIParams['useConversionMapBool'], self.UIParams['conversionMap'],
                    self.UIParams['useDisagShpBool'], self.UIParams['disagShp'], self.UIParams['disagField'],
                    self.UIParams['useExceptMap'], self.UIParams['exceptMap'])
                self.iface.messageBar().clearWidgets()
            else:
                self.alert(msgoktorun)
            
