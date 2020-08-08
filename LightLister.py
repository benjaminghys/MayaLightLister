from maya import cmds


class LightLister:
    def __init__(self):
        self.lightShapes = cmds.ls(lights=True)
        self.lightTransforms = [cmds.listRelatives(light, p=True)[0] for light in self.lightShapes]
        self.loadedData = {}

    def _update(self):
        self.lightShapes = cmds.ls(lights=True, long=True)
        self.lightTransforms = [cmds.listRelatives(light, p=True, fullPath=True)[0] for light in self.lightShapes]

    def getLights(self):
        self._update()
        dataLights = self.loadedData.keys()
        invalidLights = [light for light in self.lightTransforms if light in dataLights]
        invalidLightTypes = [self.loadedData[light]["Type"] for light in invalidLights]

        lightDisplay = [light[1:].replace('|', ' > ') for light in self.lightTransforms]

        # print "scene lights: %s" % str(self.lightTransforms)
        # print "json lights not yet added: %s" % str(invalidLights)

        return lightDisplay, self.lightShapes, invalidLights, invalidLightTypes


# todo FEATURE on list selection change, select the sel scene items for clear selection, visa versa on selecting others
# todo implement attributes on the right panel
