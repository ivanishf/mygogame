import json


def getfile(filename):
    with open(filename, "r") as fp:
        file = json.load(fp)
    return file
