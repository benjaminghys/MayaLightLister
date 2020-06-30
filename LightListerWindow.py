from PySide2 import QtCore, QtGui, QtSvg, QtWidgets
from PySide2.QtWidgets import QSizePolicy, QWidget, QTableWidget
from maya import cmds

from maya.OpenMayaUI import MQtUtil
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance

from QTableWidgetIcon import QTableWidgetIcon


class LightListerWindow(MayaQWidgetDockableMixin, QWidget):
    toolName = 'LightPresetEditor'

    def __init__(self, parent=None):
        self.__deleteInstances()
        super(self.__class__, self).__init__(parent=parent)

        titleStyleSheet = "QLabel{color: white;}" \
                          "QToolTip{background-color: rgb(180, 180, 180); font-size: 13px; font-weight: bold;}"
        toolTipStyleSheet = "QToolTip{background-color: rgb(180, 180, 180); font-size: 13px; font-weight: bold;}"

        # window settings
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setObjectName(self.__class__.toolName)
        self.setWindowTitle("Light Preset Editor - Benjamin Ghys")
        self.resize(600, 550)
        self.setMouseTracking(True)

        self.lightTransforms = []
        self.lightShapes = []
        self.loadedData = {}

        # create UI items
        outerLayout = QtWidgets.QVBoxLayout()
        mainHorizontal = QtWidgets.QHBoxLayout()
        verticalLayout = QtWidgets.QVBoxLayout()

        menuBar = QtWidgets.QMenuBar()
        # self.lightList = QListWidget()
        self.lightList = QtWidgets.QTableWidget()
        attributeGroupBox = QtWidgets.QGroupBox()
        self.splitter = QtWidgets.QSplitter()

        saveButton = QtWidgets.QPushButton("Save")
        loadButton = QtWidgets.QPushButton("Load")

        # set properties
        mainHorizontal.setSpacing(10)
        verticalLayout.setSpacing(10)
        margin = 10
        self.setContentsMargins(-5, 0, -5, 0)
        outerLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setContentsMargins(margin, margin, margin, margin)

        menuBar.setObjectName("menubar")
        menuBar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        fileMenu = menuBar.addMenu('&Light Preset')
        fileMenu.addAction("&Load...", None)
        fileMenu.addAction("&Unload...", None)
        fileMenu.addAction("&Save...", None)
        fileMenu.addAction("Save &As...", None)
        recentMenu = fileMenu.addMenu("&Recent")
        recentMenu.addAction("C:/your mom/bigJson.lightpeset", None)
        recentMenu.addAction("C:/your mom/bigJson2.lightpeset", None)
        fileMenu.addAction("Reload...", None)
        syncMenu = menuBar.addMenu('&Sync')
        syncMenu.addAction("&Scene -> Preset", None)
        syncMenu.addAction("&Preset -> Scene", None)
        sortMenu = menuBar.addMenu('S&ort')
        sortMenu.addAction("By &Type", None)  # TODO sorting
        preferencesMenu = menuBar.addMenu('&Preferences')
        # menuBar.addAction("&Help", None)  # TODO update the lists instead repaint

        self.lightList.setMinimumWidth(50)
        self.lightList.setSelectionMode(QTableWidget.ExtendedSelection)
        self.lightList.setSelectionBehavior(QTableWidget.SelectRows)
        self.lightList.setShowGrid(False)
        self.lightList.setSortingEnabled(True)
        self.lightList.setWordWrap(False)
        self.lightList.setColumnCount(3)
        self.lightList.setRowCount(5)
        self.lightList.verticalHeader().hide()
        self.lightList.verticalHeader().setDefaultSectionSize(24)
        self.lightList.horizontalHeader().setStretchLastSection(True)
        self.lightList.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.lightList.horizontalHeader().sectionResized.connect(self.sectionResized)
        # header = QHeaderView(self.lightList.horizontalHeader().orientation(), self.lightList.horizontalHeader())
        # header.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # header.setHorizontalScrollMode()

        emptyFixedTableItem = QtWidgets.QTableWidgetItem("")
        self.lightList.setHorizontalHeaderItem(0, emptyFixedTableItem)
        self.lightList.setHorizontalHeaderItem(1, emptyFixedTableItem)
        self.lightList.setHorizontalHeaderItem(2, emptyFixedTableItem)
        self.lightList.setColumnWidth(0, 30)
        self.lightList.setColumnWidth(1, self.width()/2 + 20)
        self.lightList.setColumnWidth(2, 25)

        self.lightList.setSizeAdjustPolicy(QtWidgets.QListWidget.AdjustToContents)
        self.lightList.autoFillBackground = True
        self.lightList.setIconSize(QtCore.QSize(15, 15))
        attributeGroupBox.setMinimumWidth(120)

        self.splitter.insertWidget(0, self.lightList)
        self.splitter.insertWidget(1, attributeGroupBox)
        self.splitter.setChildrenCollapsible(True)
        self.splitter.setCollapsible(0, False)
        self.splitter.splitterMoved.connect(self.sectionResized)
        self.splitter.setSizes([150, 75])

        # saveButton.pressed.connect(self.__save)
        # loadButton.pressed.connect(self.loadData)

        # arrange UI
        self.setLayout(outerLayout)
        outerLayout.addWidget(menuBar)
        outerLayout.addLayout(verticalLayout)
        verticalLayout.addLayout(mainHorizontal)
        verticalLayout.addWidget(saveButton)
        verticalLayout.addWidget(loadButton)
        mainHorizontal.addWidget(self.splitter)

        # self.show(dockable=True)

    def __deleteInstances(self):
        item = self.__class__.toolName + 'WorkspaceControl'
        if cmds.workspaceControl(item, ex=True, q=True):
            cmds.deleteUI(item)

    def sectionResized(self, pos, index):
        handleWidth = self.splitter.handleWidth()
        self.lightList.setColumnWidth(0, 30)
        self.lightList.setColumnWidth(1, pos - 60 - 2*handleWidth)
        self.lightList.setColumnWidth(2, 25)