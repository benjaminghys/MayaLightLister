from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QSizePolicy
from IconRenderer import IconRenderer
from maya import cmds


class SortFilterQTableWidgetIcon(QtCore.QSortFilterProxyModel):
    def lessThan(self, left_index, right_index):
        left_var = left_index.data(QtCore.Qt.EditRole)
        right_var = right_index.data(QtCore.Qt.EditRole)

        if isinstance(left_var, (float, int) and isinstance(right_var, (float, int))):
            return float(left_var) < float(right_var)
        if isinstance(left_var, QTableWidgetIcon and isinstance(right_var, QTableWidgetIcon)):
            return left_var.severity < right_var.severity
        return left_var < right_var


class QTableWidgetIcon(QWidget):
    def __init__(self, severity=99, path="", rendered=False, renderer=IconRenderer()):
        super(QTableWidgetIcon, self).__init__()
        self.severity = severity
        self.__scale = 20
        mainLayout = QtWidgets.QHBoxLayout()
        self.__label = QtWidgets.QLabel()

        self.renderer = renderer
        if not self.renderer.requiredChecked:
            self.renderer.renderRequired()

        if rendered:
            icon = self.renderer.getIcon(path)
        else:
            icon = QtGui.QPixmap(":/%s" % path)
            icon = icon.scaledToWidth(self.renderer.scale)

        self.setBaseSize(icon.size())
        self.__label.setPixmap(icon)
        self.__label.setFixedSize(QtCore.QSize(icon.width(), icon.height()))

        self.setFixedSize(QtCore.QSize(icon.width(), icon.height()))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        mainLayout.addWidget(self.__label)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

    def setStatus(self, **kwargs):
        if "found" in kwargs and kwargs["found"]:
            self.severity = 0
            self.__label.setPixmap(self.renderer.getIcon(checkmark=True))
        if "outdated" in kwargs and kwargs["outdated"]:
            self.severity = 1
            self.__label.setPixmap(self.renderer.getIcon(exclamation=True))
        if "add" in kwargs and kwargs["add"]:
            self.severity = 2
            self.__label.setPixmap(self.renderer.getIcon(plus=True))
        if "missing" in kwargs and kwargs["missing"]:
            self.severity = 3
            self.__label.setPixmap(self.renderer.getIcon(cross=True))

        if len(kwargs.keys()) == 0:
            cmds.warning("No status was specified")
            self.severity = 4
            self.__label.setPixmap(self.renderer.getIcon())

    # only a test
    def __lt__(self, left_index, right_index):
        left_var = left_index.data(QtCore.Qt.EditRole)
        right_var = right_index.data(QtCore.Qt.EditRole)

        if isinstance(left_var, (float, int) and isinstance(right_var, (float, int))):
            return float(left_var) < float(right_var)
        if isinstance(left_var, QTableWidgetIcon and isinstance(right_var, QTableWidgetIcon)):
            return left_var.severity < right_var.severity
        return left_var < right_var
