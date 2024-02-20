#processing of user's information

from data_collection import * 
from images_mgt import *
import files_mgt as filem
import const_lists as cl


class TimeManagement():

    def __init__(self, clearvalues, TrackedTime):
        self.WindowDate = get_date()
        self.Logs_dict = filem.read_file('Day', CreatePartialDict(self.WindowDate))
        self.Current_logs = filem.read_file('Current', Create_current_log())
        if self.WindowDate != self.Logs_dict['date']:
            self.SyncTime = 0
            MoveData(self.Logs_dict)
            self.Logs_dict = filem.read_file('Day', CreatePartialDict(self.WindowDate))
            self.Current_logs = filem.read_file('Current', Create_current_log())
            TrackedTime = 0
            
        if clearvalues:
            self.Current_logs = Create_current_log() #a dict with last data (is rewritten every run) - Last dict
            delete_screens()
        #self.Last = self.Current_logs      #a dict with last data (is rewritten every run) - Last dict
        W = CurrentW()
        self.IsActive = self.Current_logs['IsActive']
        self.SyncTime = self.Current_logs['SyncTime']
        self.TotalTracked = TrackedTime
        self.WindowText = W.WindowText
        self.process_name = W.process_name
        self.WindowPosition = W.WindowSize
        self.MousePosition = get_cursor_position()
        self.WindowTime = get_time()
        #print(self.WindowTime)
        if clearvalues:
            self.Logs_dict['starttime'] = self.WindowTime
        self.WindowDate = get_date()
        self.ImageFileName = ''              #current screen file
        (self.ImageFileNameOld, self.ImageFileNameNew) = images_path()
        self.TimeDifference = get_time_difference(self.Current_logs['time'])
        if self.Current_logs:
            self.GeneralActiveTime, self.GeneralNonActiveTime = ConvertToFloat(self.Current_logs['GeneralActiveTime']), ConvertToFloat(self.Current_logs['GeneralNonActiveTime'])
        else:
            self.GeneralActiveTime, self.GeneralNonActiveTime = 0, 0
            
        
                            
                            

    def add_data(self):
        #main function
        CL, Ind = self.calculate_data()
        self.write_data(CL, Ind)
        filem.write_file(self.Logs_dict, 'Day')
        filem.write_file(self.Current_logs, 'Current')
        


    def calculate_data(self):
        #if a user changed Mouse Position or Window Position then write the time to the active duration
        #if a user did not change Mouse Position or Window Position then make PrintScreens

        
        CL,Ind = self.get_current_log()      
        #dict of the found log {'text': self.WindowText, 'activeduration': activeduration,'nonactiveduration': nonactiveduration}      


                            
        if self.user_did_actions():
            self.calculate_duration(CL, True)        #active time calculation
            self.IsActive = 1
            if self.Current_logs['ImageFileName']:
                delete_screens()
                self.Current_logs['ImageFileName'] = ''
        else:                     
            S = ScreenImage(self.WindowPosition, self.Current_logs['ImageFileName'])
            if S.ScreenChanged:
                #print('yes - ', self.WindowTime)
                self.calculate_duration(CL, True)         #active time calculation
                self.IsActive = 1
            else:
                self.calculate_duration(CL, False)       #nonactive time calculation
                self.IsActive = 0
            self.ImageFileName = S.ScreenPath


          
        return CL, Ind
            


    def user_did_actions(self):
        return (self.Mouse_Position_Changed() or self.Window_Position_Changed())
        


    def calculate_duration(self, l, Active):
        #fuction for active and nonactive time calculation

        #self.GeneralActiveTime shows how much time a user is working on computer
        #self.GeneralNonActiveTime shows how much time a user is NOT working on computer
        """ #the program will show a notification about break when self.GeneralActiveTime >= 45 min.
        #if a user was NOT active for <=30 sec (AllowedNonActive), then self.GeneralActiveTime still continues to increase
        #else self.GeneralActiveTime becomes 0 and calculation starts from the beginning. """

        
        if self.TimeDifference < cl.CalculateDataDuration + cl.AllowingTimeToStuck:
            #exclude the cases when a user came back from LockApp.exe 
            if Active:
                l['activeduration'] += self.TimeDifference
                self.GeneralActiveTime += self.TimeDifference
                self.GeneralNonActiveTime = 0
                self.SyncTime += self.TimeDifference
            else:
                l['nonactiveduration'] += self.TimeDifference
                self.GeneralNonActiveTime += self.TimeDifference
                self.GeneralActiveTime = 0
        else:
            l['nonactiveduration'] += self.TimeDifference
            self.GeneralActiveTime = 0
            self.GeneralNonActiveTime = 0
        #print('GeneralActiveTime - ', self.GeneralActiveTime, 'GeneralNonActiveTime - ', self.GeneralNonActiveTime)


                
                

    def get_current_log(self):
        #find existing log with 'text' = self.WindowText or create a new one
        L = self.Logs_dict['logs']
        i = 0
        for l in L:
            if l['text'] == self.WindowText:
                return l,i
            i += 1
        return self.create_new_item(0, 0), None
                
                

    def write_data(self, new_item, Ind):
        if Ind is not None:
            self.Logs_dict['logs'][Ind] = new_item
        else:
            self.Logs_dict['logs'].append(new_item)
        self.Current_logs = {'text': self.WindowText,
                             'time': self.WindowTime,
                             'MousePosition': self.MousePosition,
                             'WindowPosition': self.WindowPosition,
                             'ImageFileName' : self.ImageFileName,
                             'GeneralActiveTime': self.GeneralActiveTime,
                             'GeneralNonActiveTime': self.GeneralNonActiveTime,
                             'IsActive': self.IsActive,
                             'TrackedTime': self.TotalTracked,
                             'SyncTime': self.SyncTime,
                             'date': self.WindowDate}
        

        

    def create_new_item(self, activeduration, nonactiveduration):
        new_item = {'text': self.WindowText, 'process': self.process_name, 'activeduration': activeduration,
                                          'nonactiveduration': nonactiveduration}
        return new_item



    def Mouse_Position_Changed(self):
        if self.Current_logs:
            return(self.Current_logs['MousePosition'] != self.MousePosition) or (self.WindowText != self.Current_logs['text'])
        else:
            return True
    


    def Window_Position_Changed(self):
        if self.Current_logs:
            return(tuple(self.Current_logs['WindowPosition']) != self.WindowPosition)
        else:
            return True


def CreatePartialDict(date):
    return {'date': date, 'starttime': '', 'logs':[]}

def Create_current_log():
    return {'text': '',
            'time': '',
            'MousePosition': [0, 0] ,
            'WindowPosition': (0, 0, 0, 0),
            'ImageFileName' : '',
            'GeneralActiveTime': 0,
            'GeneralNonActiveTime': 0,
            'IsActive': True,
            'TrackedTime': 0,
            'SyncTime': 0,
            'date': ''}


def CreateGeneralDict():
    return {'days':[]}


def MoveData(D):
    #move current day logs to General logs when a new day started
    Gen_Dict = filem.read_file('General', CreateGeneralDict())   
    Gen_Dict['days'].append(D)
    if len(Gen_Dict['days']) > 7:
        Gen_Dict['days'].remove(Gen_Dict['days'][0])
    filem.write_file(Gen_Dict,'General')
    filem.EraseFile('Day')
    filem.EraseFile('Current')

def ConvertToFloat(InputValue):
    try:
        ConvertedValue = float(InputValue)
        return ConvertedValue
    except:
        raise TypeError("Only float numbers are allowed for time")

