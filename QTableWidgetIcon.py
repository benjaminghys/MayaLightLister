from PySide2 import QtCore, QtGui, QtWidgets
import IconRenderer as ICO
from maya import cmds
from copy import copy


class QTableWidgetIconDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent, tableWidget):
        # type: (QTableWidgetIconDelegate, None, QtWidgets.QTableWidget) -> None
        self.tableWidget = tableWidget
        super(QTableWidgetIconDelegate, self).__init__(parent)
        self.count = 0

    def paint(self, painter, option, index, *args):
        # type: (QtGui.QPainter, QtWidgets.QStyledItemDelegate, QtCore.QModelIndex, list) -> None

        item = self.tableWidget.item(index.row(), index.column())
        if not isinstance(item, QTableWidgetIcon):
            cmds.warning("row %s col %s is not QTableWidgetIcon, skipping" % (str(index.row()), str(index.column())))
            QtWidgets.QItemDelegate.paint(self, painter, option, index)
            return
        # print "row %s col %s is QTableWidgetIcon" % (str(index.row()), str(index.column()))

        if option.state & QtWidgets.QStyle.State_Selected:
            if item.isLightIcon:
                gradientStart = option.rect.topLeft()
                gradientEnd = option.rect.topRight()
                gradientWidth = option.rect.width()
                gradientStart.setX((gradientWidth / 2) + gradientStart.x())
            else:
                gradientStart = option.rect.topRight()
                gradientEnd = option.rect.topLeft()
                gradientWidth = option.rect.width()
                gradientStart.setX(gradientStart.x() - (gradientWidth / 2))

            gradient = QtGui.QLinearGradient(gradientStart, gradientEnd)
            gradient.setColorAt(0, QtGui.QColor(43, 43, 43))
            gradient.setColorAt(1, QtGui.QColor(82, 133, 166))
            painter.fillRect(option.rect, gradient)

        iconRect = copy(option.rect)
        if not item.isLightIcon and item.severity != 4:
            iconHeight = iconRect.height() * 0.7
            iconRect.setY(iconRect.y() + (option.rect.height() / 2 - iconHeight / 2.1))
            iconRect.setHeight(iconHeight)

        iconRect.setLeft(iconRect.x() + (iconRect.width() / 2.0 - iconRect.height() / 2.0))
        iconRect.setWidth(iconRect.height())
        painter.drawPixmap(iconRect, item.icon, item.icon.rect())


class QTableWidgetIcon(QtWidgets.QTableWidgetItem):
    def __init__(self, severity=99, path="", rendered=False, renderer=ICO.IconRenderer(), **kwargs):
        super(QTableWidgetIcon, self).__init__()
        self.severity = severity
        self.isLightIcon = False
        self.renderer = renderer
        if not self.renderer.requiredChecked:
            self.renderer.renderRequired()

        if rendered:
            self.icon = self.renderer.getIcon(kwargs)
        elif len(path) > 1:
            self.isLightIcon = True
            self.icon = self.renderer.getIcon(path)
        else:
            self.icon = self.renderer.getIcon()
            cmds.warning("Path to icon is empty and not rendered")

        self.name = path.split('.')[0]

    def setStatus(self, **kwargs):
        if "found" in kwargs and kwargs["found"]:
            self.severity = 0
            self.icon = self.renderer.getIcon(checkmark=True)
            return
        if "outdated" in kwargs and kwargs["outdated"]:
            self.severity = 1
            self.icon = self.renderer.getIcon(exclamation=True)
            return
        if "add" in kwargs and kwargs["add"]:
            self.severity = 2
            self.icon = self.renderer.getIcon(plus=True)
            return
        if "missing" in kwargs and kwargs["missing"]:
            self.severity = 3
            self.icon = self.renderer.getIcon(cross=True)
            return

        self.severity = 4
        self.icon = self.renderer.getIcon()
        if "undefined" in kwargs and kwargs["undefined"]:
            return
        cmds.warning("No status was specified")

    def __lt__(self, other):
        if isinstance(other, QTableWidgetIcon):
            if len(self.name) > 1:
                # print 'sorted by light type'
                return QtCore.QCollator().compare(self.name, other.name) > 0
            # print "sorted by severity"
            return self.severity < other.severity
        return super(QTableWidgetIcon, self).__lt__(other)
