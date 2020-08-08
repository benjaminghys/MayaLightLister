from random import randint


class LightStatus:
    Found = 0       # check mark
    Outdated = 1    # exclamation
    Add = 2         # plus
    Missing = 3     # cross
    Undefined = 4

    def __init__(self):
        pass

    @staticmethod
    def random():
        return randint(0, 4)
