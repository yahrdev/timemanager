#working with printscreens

import cv2
from PIL import ImageGrab
import files_mgt as filem
import os





class ScreenImage():
    
    def __init__(self, ScreenPosition = (0, 0, 0, 0), LastScreenPath = ''):
        self.LastScreenPath = LastScreenPath
        self.ScreenChanged = False
        self.ScreenPath = ''
        (self.Img1,self.Img2) = (None, None)
        if ScreenPosition != (0, 0, 0, 0):            
            self.ScreenPath = self.makescreen(ScreenPosition)
            (self.Img1,self.Img2) = read_image()
            self.ScreenChanged = self.Screen_Changed()
                
            

    
    def Screen_Changed(self):
        #compare two images
        if (not self.Img1 is None) and (not self.Img2 is None):
        #if self.Img1 and self.Img2:
            difference = cv2.subtract(self.Img1,self.Img2)
            b, g, r = cv2.split(difference)
            return not (cv2.countNonZero(b) == cv2.countNonZero(g) == cv2.countNonZero(r) == 0)
        else:
            return False            #if at least one of images does not exist, then there is nothing to compare

        

    def get_screen_path(self):
        #if screen1.png was written in the Last dict, then we should make a printscreen to screen2.png
        #if screen2.png was written in the Last dict or there is no image in the Last dict, then we should make a printscreen to screen1.png
        
        if images_path()[0] == self.LastScreenPath:
            return images_path()[1]
        if (images_path()[1] == self.LastScreenPath) or (self.LastScreenPath == ''):
            return images_path()[0]



    def makescreen(self, ScreenPosition):
        try:
            snapshot = ImageGrab.grab(bbox = ScreenPosition)
            screen_path = self.get_screen_path()
            snapshot.save(screen_path)
            #self.testscreen(snapshot)
            return screen_path
        except:
            return ''
        
        
    def testscreen(self, snapshot):
        try:
            #teststart
            k = 1
            testpath = "to remove/screens/screen" + str(k) + ".png"
            while os.path.exists(testpath):
                k += 1
                testpath = "to remove/screens/screen" + str(k) + ".png"
            else:
                snapshot.save(testpath)
                print(testpath)
            #testend
        except:
            raise TypeError("Can not make TEST screen")


    

def images_path():
    #return ('mediafiles/screen1.png', 'mediafiles/screen2.png') #default images names
    return (filem.GetFileName('Image1'), filem.GetFileName('Image2'))

def read_image():
    ImgArray = images_path()
    (Im1, Im2) = (None, None)
    if os.path.exists(ImgArray[0]):
        Im1 = cv2.imread(ImgArray[0])
    if os.path.exists(ImgArray[1]):
        Im2 = cv2.imread(ImgArray[1])
    return (Im1, Im2)

def delete_screens():
    filem.DeleteFiles(images_path())



#A = ScreenImages()
#print(A.changes_score())
#makescreen()
        
