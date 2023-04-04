import json
import math
def writeJson(fileName, data):
    with open(fileName, "w") as userWriteData:
        json.dump(data, userWriteData)
def readJson(fileName):
    with open(fileName, "r") as userReadData:
        return(json.load(userReadData))
    
def scaleValid(scales):
    if type(scales) != list:
        return False
    if len(scales) != 3:
        return False
    for i in range(3):
        if type(scales[i]) != int and type(scales[i]) != float:
            return False
        if scales[i] <= 0:
            return False
    return True

def translateValid(translate):
    if type(translate) != list:
        return False
    if len(translate) != 3:
        return False
    for i in range(3):
        if type(translate[i]) != int and type(translate[i]) != float:
            return False
    return True

def rotateValid(rotate):
    if type(rotate) != list:
        return False
    if len(rotate) != 3:
        return False
    for i in range(3):
        if type(rotate[i]) != int and type(rotate[i]) != float:
            return False
        if rotate[i] < 0 or rotate[i] > 2*math.pi:
            return False
    return True

def resolutionValid(resolution):
    if type(resolution) != list:
        return False
    if len(resolution) != 2:
        return False
    for i in range(2):
        if type(resolution[i]) != int:
            return False
        if resolution[i] <= 0:
            return False
    return True
def focalPointValid(focalPoint):
    if type(focalPoint) != list:
        return False
    if len(focalPoint) != 3:
        return False
    for i in range(3):
        if type(focalPoint[i]) != int and type(focalPoint[i]) != float:
            return False
    return True
def diffuseChildrenValid(diffuseChildren):
    if type(diffuseChildren) != list:
        return False
    if len(diffuseChildren) != 2:
        return False
    for i in range(2):
        if type(diffuseChildren[i]) != int:
            return False
        if diffuseChildren[i] < 0:
            return False
    return True
def subRaysValid(subRays):
    if type(subRays) != list:
        return False
    if len(subRays) != 2:
        return False
    for i in range(2):
        if type(subRays[i]) != int:
            return False
        if subRays[i] < 1:
            return False
    return True
def ivityValid(ivity):
    if type(ivity) != int and type(ivity) != float:
        return False
    if ivity < 0 or ivity > 1:
        return False
    return True
def maxBouncesDepthValid(maxBouncesDepth):
    if type(maxBouncesDepth) != int and type(maxBouncesDepth) != float:
        return False
    if maxBouncesDepth < 0:
        return False
    return True
def STLnameValid(STLname):
    if type(STLname) != str:
        return False
    if STLname[-4:] != ".stl":
        return False
    return True
def validateConfig(config):
    for scales in config["objScale"]:
        if not scaleValid(scales):
            print("Invalid value for objScale in config.json")
            exit()
    scales = config["lightScale"]
    if not scaleValid(scales):
        print("Invalid value for lightScale in config.json")
        exit()
    for translate in config["objTranslate"]:
        if not translateValid(translate):
            print("Invalid value for objTranslate in config.json")
            exit()
    translate = config["lightTranslate"]
    if not translateValid(translate):
        print("Invalid value for lightTranslate in config.json")
        exit()
    for rotate in config["objRotate"]:
        if not rotateValid(rotate):
            print("Invalid value for objRotate in config.json")
            exit()
    rotate = config["lightRotate"]
    if not rotateValid(rotate):
        print("Invalid value for lightRotate in config.json")
        exit()
    if not resolutionValid(config["resolution"]):
        print("Invalid values for resolution in config.json")
        exit()
    if not focalPointValid(config["focalPoint"]):
        print("Invalid values for focalPoint in config.json")
        exit()
    if not diffuseChildrenValid(config["diffuseChildren"]):
        print("Invalid values for diffuseChildren in config.json")
        exit()
    if not subRaysValid(config["subRays"]):
        print("Invalid values for subRays in config.json")
        exit()
    if not ivityValid(config["surfaceReflectivity"]):
        print("Invalid value for surfaceReflectivity in config.json")
        exit()
    if not ivityValid(config["surfaceDiffusivity"]):
        print("Invalid value for surfaceDiffusivity in config.json")
        exit()
    if not maxBouncesDepthValid(config["maxBounces"]):
        print("Invalid value for maxBounce in config.json")
        exit()
    if not maxBouncesDepthValid(config["maxDiffDepth"]):
        print("Invalid value for maxDiffDepth in config.json")
        exit() 
    for stl in config["stlFiles"]:
        if not STLnameValid(stl):
            print("Invalid value for STLname in config.json")
            exit()
def getConfig():
    global config
    config = readJson("./config.json")
    config["cameraSize"] = [50,50]
    config["glossyChildren"] = 0
    config["surfaceGlossyness"] = 0
    validateConfig(config)