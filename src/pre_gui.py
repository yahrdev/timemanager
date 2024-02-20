#collecting data for GUI

import files_mgt as fm
import app_logic as al
import data_collection as dc
import re



def GetAppHeaders(SelectedDate):
    AppHeadersDict, AppLines = CreateAppHeaderArrays(SelectedDate)
    if AppHeadersDict:
        NewFormatedArray = list(AppHeadersDict.values())
        AppHeaders = []
        AppPercentHeaders = []
        ActiveTotal = 0

        if len(NewFormatedArray) > 0: 
            for i in range(len(NewFormatedArray)):
                ActiveTotal += al.ConvertToFloat(NewFormatedArray[i][1])
                AppName = NewFormatedArray[i][0]
                ActiveLocal = GetTimeString (NewFormatedArray[i][1])
                NonActiveLocal = GetTimeString (NewFormatedArray[i][2])
                AppHeaders.append((AppName, ActiveLocal, NonActiveLocal))

                

        if ActiveTotal > 0:
            if len(AppPercentHeaders) > 0: 
                for i in range(len(AppPercentHeaders)):
                    AppPercentHeaders[i][1] = (al.ConvertToFloat(AppPercentHeaders[i][1])/ActiveTotal)*100
                    AppPercentHeaders[i][2] = 0
                    AppPercentHeaders[i] = tuple(AppPercentHeaders[i])


        if ActiveTotal > 0:
            if len(NewFormatedArray) > 0: 
                for i in range(len(NewFormatedArray)):
                    AppName = NewFormatedArray[i][0]
                    ActiveLocal = (al.ConvertToFloat(NewFormatedArray[i][1])/ActiveTotal)*100
                    NonActiveLocal = 0
                    AppPercentHeaders.append((AppName, ActiveLocal, NonActiveLocal))



        #the tuple AppHeaders is created from AppHeadersDict. It has formated time
        #AppPercentHeaders is used in Diagram

        return sorted(AppHeaders), AppLines, AppPercentHeaders
    return [], [], []


def CreateAppHeaderArrays(SelectedDate):
    AppHeadersDict = dict()
    AppLines = dict()
    Big_Array = GetArrayOnDate(SelectedDate) #read logs for selected day
    if Big_Array:
        AppLines = dict()
        ActiveTotal = 0
        NonActiveTotal = 0       
        if 'logs' in Big_Array:
            for LocalDict in Big_Array['logs']:
                if al.ConvertToFloat(LocalDict['activeduration']) > 0:
                
                    AppName, AppText = GetAppNameText(LocalDict['text']) 
                    #print(LocalDict['text'], LocalDict['process'])

                    #get App Name from logs (initially Title consists from App Name, 
                        #tabs name, site name etc)
                    #AppText is details like tabs name, site name etc
                    
                    if AppName != '':
                        if AppName in AppHeadersDict:
                            (ActiveTotal, NonActiveTotal) = (AppHeadersDict[AppName][1], AppHeadersDict[AppName][2])
                        else:
                            (ActiveTotal, NonActiveTotal) = (0, 0)
                        #AppHeadersDict consists of AppName and general time of using for each of it

                        ActiveTotal += al.ConvertToFloat(LocalDict['activeduration'])
                        NonActiveTotal += al.ConvertToFloat(LocalDict['nonactiveduration'])
                        

                        AppHeadersDict[AppName] = [AppName, ActiveTotal, NonActiveTotal]
                        LocalDict['text'] = AppText
                        LocalDict['activeduration'] = GetTimeString(al.ConvertToFloat(LocalDict['activeduration']))
                        LocalDict['nonactiveduration'] = GetTimeString(al.ConvertToFloat(LocalDict['nonactiveduration']))
                        del LocalDict['process']
                        if AppText:
                            if AppName in AppLines:
                                AppLines[AppName].append(LocalDict)
                            else:
                                AppLines[AppName] = [LocalDict, ]
                            #AppLines consists of details like tabs name, site name etc and formated time of using

    return AppHeadersDict, AppLines




def GetArrayOnDate(Selecteddate):
    #get information for specified date
    if Selecteddate != dc.get_date():
        Gen_Dict = fm.read_file('General', al.CreateGeneralDict())
        if 'days' in Gen_Dict:
            for d in Gen_Dict['days']:
                if d['date'] == Selecteddate:
                    return d
        Last_logs = fm.read_file('Day', al.CreatePartialDict(dc.get_date()))
        if Selecteddate == Last_logs['date']:
            return Last_logs
    else:
        Last_logs = fm.read_file('Day', al.CreatePartialDict(dc.get_date()))
        if Selecteddate == Last_logs['date']:
            return Last_logs
    
  
def SearchingAppInCatalog(TextVal = ''):
    #searching apps/sites names in the catalog
    ResultParent = ''
    ResultSecondParent = ''
    GeneralProgramsList = fm.read_file('Programs_data', {}) 

    #if YouTube (site) was found then it will be reflected in Gui under YouTube, not under Google Chrome (program)
  
    if (TextVal) and (GeneralProgramsList['programs']):
        ResultParent, TextVal = SearchParentInLists(GeneralProgramsList['programs'], TextVal, 1)

        if not ResultParent:
            ResultParent, TextVal = SearchParentInLists(GeneralProgramsList['programs'], TextVal, 2)

        if not ResultParent:
            ResultParent, TextVal = SearchParentInLists(GeneralProgramsList['programs'], TextVal, 3)

    if (TextVal) and (GeneralProgramsList['sites']):
        ResultSecondParent, TextVal = SearchParentInLists(GeneralProgramsList['sites'], TextVal, 1)

        if not ResultSecondParent:
            ResultSecondParent, TextVal = SearchParentInLists(GeneralProgramsList['sites'], TextVal, 2)

        if not ResultSecondParent:
            ResultSecondParent, TextVal = SearchParentInLists(GeneralProgramsList['sites'], TextVal, 3)


    TextVal = TextVal.strip()
    if ResultSecondParent:
        return ResultSecondParent, TextVal
    elif ResultParent:
        return ResultParent, TextVal
    else:
        return '', ''
    

def SearchParentInLists(L, TextVal, Step):
    ResultParent = ''
    FoundPart = ''
    DoNotRemove = False
    for p in L:
        if Step == 1:                                           #searching ' - Google Chrome - '
            SearchResult = re.search(r'(^|\-\s)' + p + '($|\s\-)', TextVal) 
            if SearchResult:
                FoundPart = SearchResult.group(0)

        else:                                                     #searching '|Google Chrome|'
            SearchResult = re.search(r'(^|\W)' + p + '($|\W)', TextVal) 
            if SearchResult:
                FoundPart = SearchResult.group(0)
                if (FoundPart[0] == ' ')|(FoundPart[len(FoundPart) -1] == ' '):
                    DoNotRemove = True
                              
        if FoundPart:
            ResultParent = p
            if not DoNotRemove: 
                TextVal = TextVal.replace(FoundPart, ' ')
                TextVal = TextVal.strip()
            return ResultParent, TextVal
    return ResultParent, TextVal


def GetAppNameText(InputText):
    try:
        if InputText:
            AppName, AppText = SearchingAppInCatalog(InputText)
            if not AppName:
                AppTitleList = InputText.split(' - ') 
                            #example of text: 'gui_mgt.py - timemanagement - Visual Studio Code'
                AppName = AppTitleList[0] 
                        #App Name is the last (Visual Studio Code)
                if len(AppTitleList) > 2:
                    AppText = ' - '.join(AppTitleList[1:len(AppTitleList)])
                else:
                    AppText = AppTitleList[len(AppTitleList) - 1]
            return AppName, AppText
        else:
            return '', ''
    except:
        raise TypeError("Can not get Application Name or Text")
    

def GetDatesList():
    #get available dates list
    Gen_Dict = fm.read_file('General', al.CreateGeneralDict())
    DateList = []
    if 'days' in Gen_Dict:
        for d in Gen_Dict['days']:
            DateList.append(d['date'])
    Last_Dict = fm.read_file('Day', al.CreatePartialDict(dc.get_date()))
    if (Last_Dict['date'] != '') & (Last_Dict['date'] != dc.get_date()):
        DateList.append(Last_Dict['date'])
    DateList.append(dc.get_date())
    return list(reversed(DateList))


def GetActive(ForTimer):
    #check whether the user is active now
    Current_Array = fm.read_file('Current', al.Create_current_log())
    try:
        if Current_Array:
            intActive = int(Current_Array['IsActive'])
            ActiveTime = int(Current_Array['GeneralActiveTime'])
            NonActiveTime = int(Current_Array['GeneralNonActiveTime'])
            LongAbsence = (ActiveTime == 0)&(NonActiveTime == 0) #user locked screen and went out
            if ForTimer:
                return(intActive, LongAbsence)
            else:
                return intActive
        else:
            return True
    except:
        raise TypeError("Can not get current state")
    

def GetStartTime():
    #for Today Tracked value
    Today = dc.get_date()
    Current_Array = fm.read_file('Current', al.Create_current_log())
    try:
        if 'date' in Current_Array:
            if Today == Current_Array['date']:
                intTracked = int(Current_Array['TrackedTime'])
                return intTracked
        return 0
    except:
        raise TypeError("Can not get current time")
    

    
def SyncTimeTotal():
    #for Today Tracked value sync
    try:
        Big_Array = fm.read_file('Day', al.CreatePartialDict(dc.get_date()))
        SyncTime = 0
        if Big_Array:
            
            if 'logs' in Big_Array:
                for LocalDict in Big_Array['logs']:
                    SyncTime += al.ConvertToFloat(LocalDict['activeduration'])
        return SyncTime

    except:
        return 0


def resetandmove():
    #if it is a new day, then previous one is written to General file
    D = fm.read_file('Day', al.CreatePartialDict(dc.get_date()))
    if dc.get_date() != D['date']:
        al.MoveData(D)


def GetGUIData():
    #get titles, label names, button names etc for GUI
    AllDataDict = fm.read_file('GUI_data', {})
    TitlesDict = AllDataDict["WindowTitles"]
    DescrDict = AllDataDict["WindowDescriptions"]
    ButtonsDict = AllDataDict["Buttons"]
    return TitlesDict, DescrDict, ButtonsDict


def GetTimeInFormat(TimeSec, GetSec=False):
    #convert seconds to understandable format for a user
    h, s = divmod(TimeSec, 3600)
    if GetSec:
        m, s = divmod(s, 60)
        return (int(h), int(m), int(s))
    else:
        m = round(s/60)
        return (int(h), int(m))
    

def GetTimeString(TimeSec):
    timeTuple = GetTimeInFormat(TimeSec)
    if timeTuple:
        return '{0}h {1}m'.format(*timeTuple) #format should be like 1h 5m



def job(clearvalues, TrackedTime):
    #clearvalues for the first run in order to start from very beginning
    T = al.TimeManagement(clearvalues, TrackedTime)
    T.add_data()
     

def stop_job():
    global StopJob
    StopJob = True


