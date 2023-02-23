import json
def writeJson(fileName, data):
    with open(fileName, "w") as userWriteData:
        json.dump(data, userWriteData)
def readJson(fileName):
    with open(fileName, "r") as userReadData:
        return(json.load(userReadData))
def getConfig():
    global config
    config = readJson("./config.json")