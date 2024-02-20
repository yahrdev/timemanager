#reading/writting files

import json
import os.path
import sys


def read_file(FileType, DefaultDict):
    Dict = DefaultDict
    FileName = GetFileName(FileType)
    if not os.path.isfile(FileName):
        with open(FileName, 'w', encoding="utf-8") as f: #create if it does not exist
            f.close()
    f = open(FileName, 'r')
    if os.path.getsize(FileName):  #if it is not empty
        Dict = json.load(f)
    f.close()
    return Dict

def write_file(Dict, FileType):
    f = open(GetFileName(FileType), "w")
    json.dump(Dict, f)
    f.close()

    

def EraseFile(FileType):
    open(GetFileName(FileType), "w").close()

def DeleteFiles(pathList):
    for pathI in pathList:
        if os.path.exists(pathI):
            os.remove(pathI)


def GetPath(small_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
        #base_path = os.path.dirname(__file__)
        #print(base_path)
    return os.path.join(base_path, small_path)


def GetFileName(FileType):
    if FileType == 'Day':
        return GetPath('data') + '\Day_logs.json'
    if FileType == 'Current':
        return GetPath('data') + '\Current_Data.json'
    if FileType == 'General':
        return GetPath('data') + '\General_logs.json'
    if FileType == 'GUI_data':
        return GetPath('data') + '\English_data.json'
    if FileType == 'Programs_data':
        return GetPath('data') + '\Programs_list.json'
    if FileType == 'Alarm_Sound':
        return GetPath('mediafiles') + '/126505.wav'
    if FileType == 'IconImg':
        return GetPath('mediafiles') + '/clock.png'
    if FileType == 'AlarmPic':
        return GetPath('mediafiles') + '/break-time.png'
    if FileType == 'ArrowPic':
        return GetPath('mediafiles') + '\arrow-down-flat-greyscale-icon-vector.jpg'
    if FileType == 'Image1':
        return GetPath('mediafiles') + '\screen1.png'
    if FileType == 'Image2':
        return GetPath('mediafiles') + '\screen2.png'







