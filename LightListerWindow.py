from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy, QTableWidget, QTableWidgetItem
import maya.OpenMayaUI as MayaUI
import shiboken2

from maya import cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import QTableWidgetIcon as QTWI
import IconRenderer as ICO
import LightStatus as LS
import LightLister as LL


class AttributeBox(QtWidgets.QLineEdit):
    intField = 0
    floatField = 1
    boolField = 2

    def __init__(self, fieldType, value=0, parent=None):
        super(AttributeBox, self).__init__(parent)

        self.setToolTip(
            "Hold and drag middle mouse button to adjust the value\n"
            "(Hold CTRL or SHIFT change rate)")

        self.min = None
        self.max = None
        self.steps = 1
        self.value_at_press = None
        self.pos_at_press = None

        if fieldType == self.intField:
            self.setValidator(QtGui.QIntValidator(parent=self))
        elif fieldType == self.floatField:
            self.setValidator(QtGui.QDoubleValidator(parent=self))
        elif fieldType == self.boolField:
            self.setValidator(QtGui.QIntValidator(parent=self))
            self.min = 0
            self.max = 1

        self.setValue(value)
        self.fieldType = fieldType

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.MiddleButton:
            self.value_at_press = self.value()
            self.pos_at_press = event.pos()
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
        else:
            super(AttributeBox, self).mousePressEvent(event)
            self.selectAll()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.value_at_press = None
            self.pos_at_press = None
            self.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
            return
        super(AttributeBox, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() != QtCore.Qt.MiddleButton:
            return
        if self.pos_at_press is None:
            return

        delta = event.pos().x() - self.pos_at_press.x()
        delta /= 6  # Make movement less sensitive.
        delta *= self.steps * self.getStepsMultiplier(event)

        value = self.value_at_press + delta
        self.setValue(value)

        super(AttributeBox, self).mouseMoveEvent(event)

    @staticmethod
    def getMultiplier(event):
        if event.modifiers() == QtCore.Qt.CTRL:
            return 10.0
        if event.modifiers() == QtCore.Qt.SHIFT:
            return 0.1
        return 1.0

    def setMinimum(self, value):
        self.min = value
        self.setValue(self.value())

    def setMaximum(self, value):
        self.max = value
        self.setValue(self.value())

    def setSteps(self, steps):
        if self.fieldType == AttributeBox.intField:
            self.steps = int(max(steps, 1))
        else:
            self.steps = steps

    def value(self):
        if self.fieldType == AttributeBox.intField:
            return int(self.text())
        if self.fieldType == AttributeBox.floatField:
            return float(self.text())
        return int(self.text())

    def setValue(self, value):
        if self.min is not None:
            value = max(value, self.min)

        if self.max is not None:
            value = min(value, self.max)

        if self.fieldType == AttributeBox.intField:
            self.setText(str(int(value)))
            return
        if self.fieldType == AttributeBox.floatField:
            self.setText(str(float(value)))
            return
        if self.fieldType == AttributeBox.boolField:
            value = bool(round(value))
            if value:
                self.setText("on")
                return
            self.setText("off")


class LightListerWindow(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    toolName = 'LightPresetEditor'

    def __init__(self, parent=None, logic=None):
        self.__deleteInstances()
        if parent is None:
            parent = shiboken2.wrapInstance(long(MayaUI.MQtUtil.mainWindow()), QtWidgets.QMainWindow)
        super(self.__class__, self).__init__(parent=parent)

        self.logic = logic
        if self.logic is None:
            self.logic = LL.LightLister()

        titleStyleSheet = "QLabel{color: white;}" \
                          "QToolTip{background-color: rgb(180, 180, 180); font-size: 13px; font-weight: bold;}"
        toolTipStyleSheet = "QToolTip{background-color: rgb(180, 180, 180); font-size: 13px; font-weight: bold;}"

        # window settings
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setObjectName(self.__class__.toolName)
        self.setWindowTitle("LPE - Benjamin Ghys")
        self.resize(600, 550)
        self.setMouseTracking(True)

        self.iconRenderer = ICO.IconRenderer()

        # create UI items
        self.centerWidget = QtWidgets.QWidget()
        outerLayout = QtWidgets.QVBoxLayout()
        mainHorizontal = QtWidgets.QHBoxLayout()
        verticalLayout = QtWidgets.QVBoxLayout()

        menuBar = QtWidgets.QMenuBar()
        self.lightList = QtWidgets.QTableWidget()
        self.lightSBar = QtWidgets.QLineEdit()
        self.attributeSBar = QtWidgets.QLineEdit()
        self.splitter = QtWidgets.QSplitter()

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

        self.__initTable(self.lightList, 3)

        self.lightList.setItemDelegateForColumn(0, QTWI.QTableWidgetIconDelegate(self.parent(), self.lightList))
        self.lightList.setItemDelegateForColumn(2, QTWI.QTableWidgetIconDelegate(self.parent(), self.lightList))
        emptyFixedTableItem = QtWidgets.QTableWidgetItem("")
        self.lightList.setHorizontalHeaderItem(0, emptyFixedTableItem)
        self.lightList.setHorizontalHeaderItem(2, emptyFixedTableItem)
        self.lightList.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Name"))

        self.lightList.setSizeAdjustPolicy(QtWidgets.QListWidget.AdjustToContents)
        self.lightList.autoFillBackground = True
        self.lightList.setIconSize(QtCore.QSize(15, 15))
        
        # self.__initTable(self.attributeList, 2)
        # self.attributeList.setMinimumWidth(120)

        self.lightSBar.setPlaceholderText("Light filter")
        self.attributeSBar.setPlaceholderText("Attribute filter")

        # self.splitter.insertWidget(0, self.lightList)
        # self.splitter.insertWidget(1, self.attributeList)

        lightWidget = QtWidgets.QWidget()
        lightVBox = QtWidgets.QVBoxLayout(lightWidget)
        lightVBox.addWidget(self.lightSBar)
        lightVBox.addWidget(self.lightList)
        lightVBox.setContentsMargins(0, 0, 0, 0)
        self.splitter.insertWidget(0, lightWidget)

        attributeWidget = QtWidgets.QWidget()
        attributeVBox = QtWidgets.QVBoxLayout(attributeWidget)
        attributeVBox.addWidget(self.attributeSBar)
        attributeVBox.addWidget(self.attributeList)
        attributeVBox.setContentsMargins(0, 0, 0, 0)
        self.splitter.insertWidget(1, attributeWidget)

        self.splitter.setChildrenCollapsible(True)
        self.splitter.setCollapsible(0, False)
        self.splitter.splitterMoved.connect(self.sectionResized)
        self.splitter.setSizes([150, 75])

        # arrange UI
        self.centerWidget.setLayout(outerLayout)
        outerLayout.addWidget(menuBar)
        outerLayout.addLayout(verticalLayout)
        verticalLayout.addLayout(mainHorizontal)
        mainHorizontal.addWidget(self.splitter)

        # connections
        self.lightSBar.textChanged.connect(self.updateLightFilter)
        self.lightSBar.returnPressed.connect(self.updateLightFilter)

        self.setCentralWidget(self.centerWidget)
        self.resizeEvent()
        self.updateLights()
        # self.updateAttributes()

        if cmds.window("tempWindow", ex=True):
            cmds.deleteUI("tempWindow")

    def __deleteInstances(self):
        item = self.__class__.toolName + 'WorkspaceControl'
        if cmds.workspaceControl(item, ex=True, q=True):
            cmds.deleteUI(item)

    @staticmethod
    def __initTable(table, cols):
        table.setMinimumWidth(50)
        table.setSelectionMode(QTableWidget.ExtendedSelection)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setShowGrid(False)
        table.setSortingEnabled(True)
        table.setWordWrap(False)
        table.setColumnCount(cols)
        table.setRowCount(0)
        table.verticalHeader().hide()
        table.verticalHeader().setDefaultSectionSize(24)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

    def event(self, event, *args, **kwargs):
        if event is None:
            return False
        if event.type() == QtCore.QEvent.WindowActivate:
            self.updateLights()
            event.accept()
        # print event.type()
        return super(LightListerWindow, self).event(event)

    def resizeEvent(self, event=None):
        self.sectionResized(self.splitter.sizes()[0])
        if event is None:
            return True
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def sectionResized(self, pos):
        handleWidth = self.splitter.handleWidth()
        self.lightList.setColumnWidth(0, 35)
        self.lightList.setColumnWidth(1, pos - 70 - 2*handleWidth)
        self.lightList.setColumnWidth(2, 35)

    def addLight(self, index, lightType, name, status):
        # type: (int, str, str, LS.LightStatus) -> None
        if index >= self.lightList.rowCount():
            cmds.warning("extended list, rowcount went out of index")
            self.lightList.setRowCount(index + 1)

        icon, name, statusIcon = self.__createListItem(name, lightType)

        if status == LS.LightStatus.Found:
            statusIcon.setStatus(found=True)
        if status == LS.LightStatus.Outdated:
            statusIcon.setStatus(outdated=True)
        if status == LS.LightStatus.Add:
            statusIcon.setStatus(add=True)
        if status == LS.LightStatus.Missing:
            statusIcon.setStatus(missing=True)
        if status == LS.LightStatus.Undefined:
            statusIcon.setStatus(undefined=True)

        self.lightList.setItem(index, 0, icon)
        self.lightList.setItem(index, 1, name)
        self.lightList.setItem(index, 2, statusIcon)

    def updateLights(self):
        selection = self.lightList.selectedItems()
        selection = [selection[i].text() for i in range(1, len(selection), 3)]

        lights, lightShapes, dataLights, dataLightTypes = self.logic.getLights()

        self.lightList.setSortingEnabled(False)
        self.lightList.setRowCount(0)
        self.lightList.setRowCount(len(lights) + len(dataLights))

        for i in range(len(lights)):
            self.addLight(i, cmds.nodeType(lightShapes[i]), lights[i], LS.LightStatus.Found)
        for i in range(len(dataLights)):
            self.addLight(len(lights) + i, dataLightTypes[i], dataLights[i], LS.LightStatus.Undefined)

        self.lightList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        for itemName in selection:
            items = self.lightList.findItems(itemName, QtCore.Qt.MatchExactly)
            if not items:
                continue
            for item in items:
                self.lightList.selectRow(self.lightList.indexFromItem(item).row())
        self.lightList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.lightList.setSortingEnabled(True)
        self.updateLightFilter()
        
    def updateAttributes(self):
        selection = self.attributeList.selectedItems()
        selection = [selection[i].text() for i in range(0, len(selection), 2)]

        self.attributeList.setRowCount(0)
        self.attributeList.setRowCount(1)

        item = QTableWidgetItem()
        self.attributeList.setItem(0, 0, item)

    def updateLightFilter(self):
        filterText = self.lightSBar.text().lower()
        if not filterText or len(filterText) == 0:
            for i in range(self.lightList.rowCount()):
                self.lightList.setRowHidden(i, False)
            return
        filterText = filterText.split(" ")
        for i in range(self.lightList.rowCount()):
            match = False
            for j in range(self.lightList.columnCount()):
                item = self.lightList.item(i, j)
                if isinstance(item, QTWI.QTableWidgetIcon):
                    targetText = item.name
                else:
                    targetText = item.text().lower()

                for text in filterText:
                    if len(text) == 0:
                        continue
                    if text not in targetText:
                        match = False
                        break
                    match = True
                if match:
                    break
            self.lightList.setRowHidden(i, not match)

    def getSelectionList(self):
        items = self.lightList.selectedItems()
        selection = [items[i].text() for i in range(1, len(items), 3)]
        return ['|' + item.replace(" > ", "|") for item in selection]

    def __createListItem(self, name, lightType):
        item = QTableWidgetItem()
        item.setText(name)
        itemIcon = QTWI.QTableWidgetIcon(path='%s.svg' % lightType)
        statusIcon = QTWI.QTableWidgetIcon(renderer=self.iconRenderer, rendered=True)
        return itemIcon, item, statusIcon


lightLister = LightListerWindow()
lightLister.show(dockable=True, retain=False)
