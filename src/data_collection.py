#taking user's information

from ctypes import wintypes, windll, create_unicode_buffer, Structure, c_long, pointer, byref, sizeof
import time
from datetime import datetime
import psutil
import files_mgt as fm

CurrDLL = windll.user32
WindSizeDLL = windll.dwmapi


class CurrentW():

    def __init__(self):
        self.CurrW = CurrDLL.GetForegroundWindow()
        self.WindowText, FoundText = self.get_window_text()
        self.WindowSize = self.get_window_size(FoundText == '')
        
        #print(self.process_name)
        
        
        

    def get_window_text(self):
        l = CurrDLL.GetWindowTextLengthW(self.CurrW)
        buf = create_unicode_buffer(l + 1)
        CurrDLL.GetWindowTextW(self.CurrW, buf, l + 1)

        self.process_name = self.get_window_process() #we can find the process name in our catalog

        if self.process_name != '':
            Programs_Dict = fm.read_file('Programs_data', {})
            if self.process_name in Programs_Dict['processes']:
                ProcessName = Programs_Dict['processes'][self.process_name]
                if ProcessName in buf.value:
                    return buf.value, buf.value
                else:
                    return ProcessName + ' - ' + buf.value, buf.value

        if buf.value: #otherwise we can get current window name
            return buf.value, buf.value
        else:
            return None, None
            

    def get_window_process(self):
        pid = wintypes.DWORD()
        CurrDLL.GetWindowThreadProcessId(self.CurrW, byref(pid))
        process_name = psutil.Process(pid.value).name()
        return process_name.lower()



    def get_window_size(self, cutW):    
        rect = wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        WindSizeDLL.DwmGetWindowAttribute(wintypes.HWND(self.CurrW),
          wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
          byref(rect),
          sizeof(rect)
          )
        if cutW: 
            if  rect.bottom > 70:
                return (rect.left, rect.top, rect.right, rect.bottom - 70) #desktop screen
        return (rect.left, rect.top, rect.right, rect.bottom) 
    
    

class POINT(Structure):
    _fields_ = [("x", c_long),
                ("y", c_long)]

def get_cursor_position():
    point = POINT()
    result = CurrDLL.GetCursorPos(pointer(point))
    if result:  return [point.x, point.y] 
    else:       return None


def get_time():
    return time.strftime("%H:%M:%S")

def get_date():
    return time.strftime("%d.%m.%Y")

def get_time_difference(LastTime):
    #get number of seconds passed
    NewTime = datetime.strptime(time.strftime("%H:%M:%S"), "%H:%M:%S")
    if LastTime:
        OldTime = datetime.strptime(LastTime, "%H:%M:%S")
        SecDelta = abs(NewTime - OldTime)
    else:               
        SecDelta = abs(NewTime - NewTime)
        #if a Last dict does not have 'time' value then it is the first running. So, 0 seconds
    return SecDelta.total_seconds()

if __name__== '__main__':
    s = CurrentW()
    time.sleep(5)
    s.get_window_text()