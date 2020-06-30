from PySide2 import QtSvg, QtCore, QtGui
from maya import cmds
import os


class IconRenderer:
    def __init__(self, startDir=None):
        self.__startDir = startDir
        if not startDir:
            self.__startDir = os.path.join(cmds.internalVar(userScriptDir=True), "/LightLister/Icons")

        self.__checkDir()

        self.__width = self.__height = 512
        self.__thickness = self.__width / 10
        self.__goldenRatio = 0.666
        self.__scale = 20

        self.__ratio = self.__width * self.__goldenRatio
        self.__invertedRatio = self.__width * (1 - self.__goldenRatio)

        self.__loadedIcons = {}
        self.requiredChecked = False

    def getIcons(self, **kwargs):
        icons = []
        if "checkmark" in kwargs and kwargs["checkmark"]:
            icon = self.__loadIcon("checkmark.svg")
            if icon:
                icons.append(icon)
        if "cross" in kwargs and kwargs["cross"]:
            icon = self.__loadIcon("cross.svg")
            if icon:
                icons.append(icon)
        if "exclamation" in kwargs and kwargs["exclamation"]:
            icon = self.__loadIcon("exclamation.svg")
            if icon:
                icons.append(icon)
        if "plus" in kwargs and kwargs["plus"]:
            icon = self.__loadIcon("plus.svg")
            if icon:
                icons.append(icon)
        return icons

    def getIcon(self, path="", **kwargs):
        if len(path) > 0:
            icon = QtGui.QPixmap(":/%s" % path)
            return icon.scaledToWidth(self.__scale)
        if "checkmark" in kwargs and kwargs["checkmark"]:
            icon = self.__loadIcon("checkmark.svg")
            if icon:
                return icon
        if "cross" in kwargs and kwargs["cross"]:
            icon = self.__loadIcon("cross.svg")
            if icon:
                return icon
        if "exclamation" in kwargs and kwargs["exclamation"]:
            icon = self.__loadIcon("exclamation.svg")
            if icon:
                return icon
        if "plus" in kwargs and kwargs["plus"]:
            icon = self.__loadIcon("plus.svg")
            if icon:
                return icon
        return QtGui.QPixmap(":/kAlertQuestionIcon.png")

    def __loadIcon(self, path):
        if path in self.__loadedIcons:
            return self.__loadedIcons[path]

        icon = QtGui.QPixmap(os.path.join(self.__startDir, path))
        if not icon.isNull():
            self.__loadedIcons[path] = icon.scaledToWidth(self.__scale)
            return self.__loadedIcons[path]

        cmds.warning("%s not found" % path)
        return None

    def renderAll(self):
        self.renderCheckmark()
        self.renderCross()
        self.renderExclamation()
        self.renderPlus()

    def renderRequired(self):
        self.requiredChecked = True
        if not self.__checkDir():
            self.renderAll()
            return
        if not self.__fileExists("checkmark.svg"):
            self.renderCheckmark()
        if not self.__fileExists("cross.svg"):
            self.renderCross()
        if not self.__fileExists("exclamation.svg"):
            self.renderExclamation()
        if not self.__fileExists("plus.svg"):
            self.renderPlus()

    def __fileExists(self, path):
        return os.path.exists(os.path.join(self.__startDir, path))

    def __initSVGFile(self, filename):
        generator = QtSvg.QSvgGenerator()
        generator.setFileName(os.path.join(self.__startDir, filename))
        generator.setSize(QtCore.QSize(self.__width, self.__height))
        generator.setViewBox(QtCore.QRect(0, 0, self.__width, self.__height))
        painter = QtGui.QPainter(generator)
        painter.setClipRect(QtCore.QRect(0, 0, self.__width, self.__height))
        return generator, painter

    def __checkDir(self):
        if not os.path.exists(self.__startDir):
            os.makedirs(self.__startDir)
            return False
        return True

    def renderCheckmark(self):
        invertedRatio = self.__width * (1 - self.__goldenRatio)
        ratio = self.__width * self.__goldenRatio

        generator, painter = self.__initSVGFile("checkmark.svg")
        painter.translate(invertedRatio, self.__height - 2.5 * self.__thickness)
        painter.setPen(QtGui.QPen(QtCore.Qt.green, self.__thickness))
        marginRatio = ratio * 0.85
        invertedRatio *= 0.75
        painter.drawLine(QtCore.QLine(0, 0, marginRatio, -marginRatio))
        painter.drawLine(QtCore.QLine(0, 0, -invertedRatio, -invertedRatio))
        painter.end()

    def renderCross(self):
        generator, painter = self.__initSVGFile("cross.svg")
        painter.setPen(QtGui.QPen(QtCore.Qt.red, self.__thickness))
        painter.drawLine(QtCore.QLine(self.__thickness, self.__thickness, self.__width - self.__thickness, self.__height - self.__thickness))
        painter.drawLine(QtCore.QLine(self.__width - self.__thickness, self.__thickness, self.__thickness, self.__height - self.__thickness))
        painter.end()

    def renderExclamation(self):
        ratio = self.__width * self.__goldenRatio

        generator, painter = self.__initSVGFile("exclamation.svg")
        painter.setPen(QtGui.QPen(QtCore.Qt.yellow, self.__thickness))
        painter.translate(self.__width / 2, self.__thickness / 2)
        painter.drawLine(QtCore.QLine(0, 0, 0, ratio))
        painter.drawLine(QtCore.QLine(0, self.__height - self.__thickness / 2, 0, self.__height - self.__thickness))
        painter.end()
        
    def renderPlus(self):
        generator, painter = self.__initSVGFile("plus.svg")
        painter.setPen(QtGui.QPen(QtCore.Qt.white, self.__thickness))
        painter.drawLine(QtCore.QLine(self.__thickness, self.__height / 2, self.__width - self.__thickness, self.__height / 2))
        painter.drawLine(QtCore.QLine(self.__width / 2, self.__thickness, self.__width / 2, self.__height - self.__thickness))
        painter.end()

    @property
    def scale(self):
        return self.__scale
