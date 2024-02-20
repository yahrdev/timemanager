from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QSound
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from qtwidgets import AnimatedToggle
import sys
import pre_gui as m
import const_lists as cl
import files_mgt as f
import ctypes, sys

TitlesDict, DescrDict, ButtonsDict = m.GetGUIData()

class AlarmMsgBox(QMessageBox):
    #Break Alarm Window
    def __init__(self):
        super().__init__()
        self.AlarmSound = QSound(f.GetFileName('Alarm_Sound'))
        self.ArarmStarted = False
        if m.GetActive(True)[0]:
            self.ArarmStarted = True
            self.AlarmSound.play()
        self.setWindowTitle(TitlesDict["MainWindowTitle"])
        self.setWindowFlags(Qt.WindowType.Window |
                            Qt.WindowType.CustomizeWindowHint |
                            Qt.WindowType.WindowTitleHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        
        self.setText('It is time for a break!')
        self.setStyleSheet('''QMessageBox {font: bold; }
                                QPushButton {width: 130; font-size: 9pt;}''')

        self.setWindowIcon(QIcon(f.GetFileName('IconImg')))
        ImgAlarm = QPixmap(f.GetFileName('AlarmPic')).scaled(100, 100)
        self.setIconPixmap(ImgAlarm)
        self.addButton(ButtonsDict["AlarmNotify3mins"].format(cl.NotifyAfterTime), QMessageBox.ButtonRole.ActionRole)
        OKbutton = self.addButton(ButtonsDict["OKbutton"], QMessageBox.ButtonRole.ActionRole)
        self.setDefaultButton(OKbutton)



    def RunAlarmWindow(self):       
        self.exec_()
        button = self.clickedButton()
        if button is not None:
            if button.text() == ButtonsDict["AlarmNotify3mins"].format(cl.NotifyAfterTime): 
                return True
            else:
                if self.ArarmStarted:
                    self.AlarmSound.stop()
                return False
        else:
            return False
        


class TimeMgtApp(QDialog):
    #Main Window
    def __init__(self):
        super().__init__()
        self.windows = []
        self.setWindowTitle(TitlesDict["MainWindowTitle"])
        self.setFixedSize(1100, 900) #to get screen size and calculate for him
        self.setWindowIcon(QIcon(f.GetFileName('IconImg')))

        TMWidget = QTabWidget(self)
        TMWidget.setFixedSize(round(self.frameGeometry().width()), round(self.frameGeometry().height()))

#first tab:       
        self.MainWidget = QWidget(TMWidget)
        self.MainWidget.setFixedSize(round(TMWidget.frameGeometry().width()), 
                                round(TMWidget.frameGeometry().height()*99/100))

        self.MainFrameFunc()
        self.TableFrameFunc()
        

        MainLayout = QVBoxLayout()
        self.MainWidget.setLayout(MainLayout)
        MainLayout.addWidget(self.MainTimerFrame, 3)
        MainLayout.addWidget(self.TableFrameWidget, 6)
        MainLayout.addStretch(1)

        TMWidget.addTab(self.MainWidget, 'Main')


        self.MainToggleChanged(False)

#second tab: 
        self.AlarmWidget = QWidget(TMWidget)
        self.AlarmWidget.setFixedSize(round(TMWidget.frameGeometry().width()),
                                 round(TMWidget.frameGeometry().height()))
        

        self.SetupFrameFunc()
        self.TimerFrameFunc() 

        AlarmBox = QVBoxLayout(self.AlarmWidget)

        AlarmBox.addWidget(self.SetupFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        AlarmBox.addStretch(1)
        AlarmBox.addWidget(self.TimerFrame, alignment=Qt.AlignmentFlag.AlignCenter)
        AlarmBox.addStretch(2)

        TMWidget.addTab(self.AlarmWidget, 'Notifications')
        self.GlobalStop = True
        self.AlarmToggleChanged(False)

        self.trayW = QSystemTrayIcon(self)
        self.trayW.setIcon(QIcon(f.GetFileName('IconImg')))
        self.trayW.activated.connect(self.activateW)

        trayWMenu = QMenu()
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quitTimer)
        trayWMenu.addAction(quit_action)
        self.trayW.setContextMenu(trayWMenu)
        trayWMenu.setStyleSheet('background-color: #312E2E; color: white')


    def MainFrameFunc(self):
        
        self.MainTimerFrame = QFrame(self.MainWidget)
        self.MainTimerFrame.setObjectName('switchon')
        self.MainTimerFrame.setFixedSize(round(self.MainWidget.frameGeometry().width()*99/100), 
                                round(self.MainWidget.frameGeometry().height()*13/100))

        
        self.MainTimerFrame.setStyleSheet('switchon {background-color: #FAFAFA;}')
        effect = QGraphicsDropShadowEffect(offset=QPoint(2, 2), blurRadius=10, color=QColor("#bdbdbd"))
        self.MainTimerFrame.setGraphicsEffect(effect)
        MainTimerWidget = QWidget(self.MainTimerFrame) 
        #MainTimerWidget was added in order to avoid applying of QFrame styles to all child objects

        MainTimerLayout = QHBoxLayout()
        MainTimerWidget.setLayout(MainTimerLayout)
        MainTimerWidget.setStyleSheet('background-color: #FAFAFA')
        MainTimerWidget.setFixedSize(round(self.MainTimerFrame.frameGeometry().width()*98/100), 
                                round(self.MainTimerFrame.frameGeometry().height()*97/100))


        MainTimerBoxLayout = QHBoxLayout()
        MainTimerBox = QGroupBox(TitlesDict["MainGroupBox"])
        MainTimerBox.setFixedSize(round(MainTimerWidget.frameGeometry().width()*99/100), 
                                round(MainTimerWidget.frameGeometry().height()*97/100))
        MainTimerBox.setLayout(MainTimerBoxLayout)
        MainTimerBox.setStyleSheet("QGroupBox{font-size: 22px;}")                        
        

        MainDescription = QLabel()
        MainDescription.setText(DescrDict["MainGroupBoxDescr"])
        MainDescription.setFixedSize(250, 60)
        MainDescription.setStyleSheet('color: #BFBFBF')
        MainDescription.setWordWrap(True)
        self.ToggleMain = AnimatedToggle(checked_color="#78C1C0", pulse_checked_color="#78C1C0")      
        self.ToggleMain.setFixedSize(90, 70)
        self.ToggleMain.stateChanged.connect(self.MainToggleButton)
        self.OnOffMain = QLabel()
        self.OnOffMain.setFixedSize(50, 70)


        MainTimerDescription = QLabel()
        MainTimerDescription.setText(DescrDict["TodayTracked"])
        MainTimerDescription.setStyleSheet('color: #BFBFBF')
        MainTimerDescription.setFixedSize(105, 60)
        self.MainTimerLable = QLabel()
        self.MainTimerLable.setFixedSize(100, 60)
        self.StartValue = m.GetStartTime()
        TimeTuple = GetTimeInFormat(self.StartValue)
        self.MainTimerLable.setText('{:0>2}:{:0>2}:{:0>2}'.format(*TimeTuple))
        
        
        MainTimerBoxLayout.setContentsMargins (20, 0, 0, 0)
        MainTimerBoxLayout.setSpacing(0)
        MainTimerBoxLayout.addWidget(MainDescription, alignment=Qt.AlignmentFlag.AlignVCenter)
        MainTimerBoxLayout.addStretch(1)
        MainTimerBoxLayout.addWidget(self.ToggleMain, alignment=Qt.AlignmentFlag.AlignVCenter)
        MainTimerBoxLayout.addWidget(self.OnOffMain, alignment=Qt.AlignmentFlag.AlignVCenter)
        MainTimerBoxLayout.addStretch(9)
        MainTimerBoxLayout.addWidget(MainTimerDescription)
        MainTimerBoxLayout.addStretch(1)
        MainTimerBoxLayout.addWidget(self.MainTimerLable)
        MainTimerBoxLayout.addStretch(2)

        MainTimerLayout.setContentsMargins (5, 0, 5, 5)
        MainTimerLayout.addWidget(MainTimerBox) 
    



    def TableFrameFunc(self):
        self.TableFrameWidget = QFrame(self.MainWidget)
        self.TableFrameWidget.setObjectName('mainframe')
        self.TableFrameWidget.setFixedSize(round(self.MainWidget.frameGeometry().width()*97/100), 
                                round(self.MainWidget.frameGeometry().height()*81/100))
        
        
        
        self.TableFrameWidget.setStyleSheet('mainframe {background-color: #FAFAFA; }')
        effect = QGraphicsDropShadowEffect(offset=QPoint(2, 2), blurRadius=10, color=QColor("#bdbdbd"))
        self.TableFrameWidget.setGraphicsEffect(effect)

        
        self.TableWidget = QWidget(self.TableFrameWidget)
        self.TableWidget.setObjectName('tableframe')
        #TableWidget was added in order to avoid applying of QFrame styles to all child objects

        TableFrameBox = QVBoxLayout()
        self.TableWidget.setLayout(TableFrameBox)
        self.TableWidget.setFixedSize(round(self.TableFrameWidget.frameGeometry().width()*99/100), 
                                round(self.TableFrameWidget.frameGeometry().height()*98/100))  

        DateLayout = QHBoxLayout()
        TableFrameBox.addLayout(DateLayout)



        self.TableFrameWidget.setStyleSheet('background-color: white')
        self.DateList = m.GetDatesList()
        self.DateChanger = QComboBox()
        self.DateChanger.addItems(self.DateList)
        self.DateChanger.setStyleSheet('QComboBox {background-color: white; border: 1px solid; border-color: #B5B4B4; padding-left: 8px;}' +
                                       'QComboBox::drop-down { width: 30px;}' +
                                       'QComboBox QAbstractItemView {selection-background-color: #78C1C0}') 
        

        self.DateChanger.setFixedSize(150, 30)
        
    
        self.ContentOnDate = {}
        
        self.DateChanger.currentIndexChanged.connect(lambda: self.UpdateTableContent(True))
        

        DateDescription = QLabel()
        DateDescription.setText(DescrDict["ShowOnDate"])
        DateDescription.setStyleSheet('color: #BFBFBF')

        DateLayout.addStretch(1)
        DateLayout.addWidget(DateDescription)
        DateLayout.addWidget(self.DateChanger)
        

        self.TableLayoutFunc()

        self.DiagramLayoutFunc()

        self.UpdateData(True)


        self.TableTabs = QTabWidget()
        self.TableTabs.setFixedSize(round(self.TableWidget.width()), round(self.TableWidget.height()))
        self.TableTabs.addTab(self.Diagram, 'Diagram')
        self.TableTabs.addTab(self.Table, 'Details')
        self.TableTabs.setStyleSheet('''QTabBar::tab {background-color: #FAFAFA;} 
                                     QTabBar::tab:selected {background-color: #C0C3C3;} 
                                     QTabWidget::pane {border: none; padding-top: 20px}''')
        

        TableFrameBox.addWidget(self.TableTabs, alignment=Qt.AlignmentFlag.AlignHCenter)

        
        self.TableWidget.setStyleSheet(''' 
        QTabWidget::tab-bar {
            alignment: center;
        } ''')


    def DiagramLayoutFunc(self):

        self.Pieseries = QPieSeries()

        self.Chart = QChart()
        self.Chart.addSeries(self.Pieseries)
        self.Chart.legend().hide()

        self.Diagram = QChartView(self.Chart)  
        self.Diagram.setRenderHint(QPainter.Antialiasing)
        self.Diagram.setStyleSheet('background-color: white')




    def TableLayoutFunc(self):
        
        self.Table = QTreeWidget()
        self.Table.setStyleSheet('''QTreeWidget {background-color: white; border: 1px solid; border-color: #B5B4B4;}
                                    QTreeWidget::item {border: 0px; padding: 5px; color: black }
                                    QTreeWidget::item:focus {border: 0px; color: black; background-color:transparent;}''')
        self.Table.setFixedSize(round(self.TableWidget.frameGeometry().width()*98/100), 
                                round(self.TableWidget.frameGeometry().height()*85/100))  

        Headers = QHeaderView(Qt.Orientation.Horizontal, self.Table)
        Headers.setStyleSheet('''QHeaderView {border: none} 
                   QHeaderView::section {background-color: #78C1C0; color: white; padding-left: 13px; padding-top: 5px; font: bold; font-size: 9pt}''')
        Headers.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.Table.setHeader(Headers)
        self.Table.setColumnCount(2) 
        self.Table.setHeaderLabels([DescrDict["AppNameHeader"], DescrDict["ActiveHeader"]])
    
        
        ColumnWidthPers = [81.8,18]
        self.Table.setColumnWidth(0, int(self.Table.width() * ColumnWidthPers[0]/100))
        self.Table.setColumnWidth(1, int(self.Table.width() * ColumnWidthPers[1]/100))

    
            
    
    def UpdateData(self, ClearTable):
        MainNames, ContentItems, PercentHeaders = m.GetAppHeaders(self.DateChanger.currentText())
        self.AddTableRows(ClearTable, MainNames, ContentItems)
        self.UpdateDiagram(PercentHeaders)




    def AddTableRows(self, ClearTable, MainNames, ContentItems):

        if ClearTable:
            self.Table.clear()

        if (MainNames) and (ContentItems):
            for j in range(len(MainNames)): 
                if ClearTable:
                    TableItem = QTreeWidgetItem(self.Table)
                else:
                    self.Table.setCurrentItem(None)
                    ItemsList = self.Table.findItems(MainNames[j][0], Qt.MatchFlag.MatchExactly, 0) #find parent items
                    if ItemsList:
                        TableItem = ItemsList[0]
                    else:
                        TableItem = QTreeWidgetItem(self.Table)

                font = QFont('', 9, 0, False)
                TableItem.setFont(0, font)
                for i in range(2):
                    TableItem.setText(i, MainNames[j][i]) #add/update parent items
                ChildRowsTuple = ()
                if MainNames[j][0] in ContentItems: 
                    ChildRowsTuple = ContentItems[MainNames[j][0]] #find parent name and his child in general array
                
                for p in range(len(ChildRowsTuple)):
                    ChiledFound = False
                    if ClearTable:
                        ChiledItem = QTreeWidgetItem(TableItem)
                    else:                   
                        self.Table.setCurrentItem(None)
                        CItemsList = self.Table.findItems(ChildRowsTuple[p]["text"], Qt.MatchFlag.MatchExactly | Qt.MatchFlag.MatchRecursive, 0)
                        #finding child in child items and not only
                        if len(CItemsList) > 0:
                            CItemsList = [k for k in CItemsList if k != TableItem] #exclude parent
                        if CItemsList:      
                            s = 0
                            FoundParent = False 
                            while (not FoundParent) and (s < len(CItemsList)):  
                                ParentItem = CItemsList[s].parent()                                            
                                if ParentItem:
                                    FoundParent = (ParentItem.text(0) == MainNames[j][0])
                                s += 1
                            #exclude cases when child name was found in both parent and child items
                                
                            if ParentItem:
                                ChiledItem = CItemsList[0]
                                ChiledFound = True
                        if not ChiledFound:
                            ChiledItem = QTreeWidgetItem(TableItem)

                    i = 0
                    ChiledRow = ChildRowsTuple[p] 
                    for k in ChiledRow:                                  
                        ChiledItem.setText(i, ChiledRow[k])
                        i += 1
                    if not ChiledFound:
                        TableItem.addChild(ChiledItem)
        
    
    def UpdateDiagram(self, PercentHeaders):
        self.Pieseries.clear()
    
        StartColorNumber = cl.DiagramStartingColor
    
        if PercentHeaders:
            SelectedValues = [i for i in PercentHeaders if i[1] > cl.DiagramHighPercent]
            GeneralOtherPercent = 0
            for Line in PercentHeaders:
                if Line[1] > cl.DiagramHighPercent:
                    Oneslice = self.Pieseries.append(Line[0], Line[1])
                    Oneslice.setBrush(QColor(StartColorNumber, 187, 185))
                    if len(SelectedValues) > 0:
                        StartColorNumber += round((cl.DiagramColorRestriction - cl.DiagramStartingColor)/len(SelectedValues))
                    else:
                        StartColorNumber += cl.DiagramColorStep

                    if StartColorNumber > cl.DiagramColorRestriction:
                        StartColorNumber = cl.DiagramStartingColor                  
                else:
                    GeneralOtherPercent += Line[1]

            if GeneralOtherPercent > 0:
                Oneslice = self.Pieseries.append('Others', GeneralOtherPercent)
                Oneslice.setBrush(QColor(*cl.DiagramOtherColor))
        else:
            Oneslice = self.Pieseries.append('Nothing yet', 100)
            Oneslice.setBrush(QColor(cl.DiagramStartingColor, 187, 185))


                

        self.Pieseries.setLabelsVisible()




    def SetupFrameFunc(self):
        self.SetupFrame = QFrame(self.AlarmWidget)
        self.SetupFrame.setObjectName('setupframe')
        self.SetupFrame.setFixedSize(round(self.AlarmWidget.frameGeometry().width()*98/100), 
                                round(self.AlarmWidget.frameGeometry().height()*19/100))
        
        self.SetupFrame.setStyleSheet('setupframe {background-color: #FAFAFA; }')

        effect = QGraphicsDropShadowEffect(offset=QPoint(2, 2), blurRadius=10, color=QColor("#bdbdbd"))
        self.SetupFrame.setGraphicsEffect(effect)
        SetupWidget = QWidget(self.SetupFrame)
        SetupWidget.setFixedSize(round(self.SetupFrame.frameGeometry().width()*99/100), 
                                round(self.SetupFrame.frameGeometry().height()*99/100))
        
        #SetupWidget was added in order to avoid applying of QFrame styles to all child objects

    
        SetupBox = QHBoxLayout(SetupWidget)
        SetupWidget.setStyleSheet('background-color: #FAFAFA')

    #first part of SetupBox
        AlarmMainLayout = QVBoxLayout()
        SetupBox.addLayout(AlarmMainLayout, 1)

        AlarmDescription = QLabel(SetupWidget)
        AlarmDescription.setText(TitlesDict["BreakTimerName"])
        AlarmDescription.setStyleSheet('padding-left: 1')
        font = QFont("Times", 13, 3, False)
        font.bold = True
        AlarmDescription.setFont(font)
        AlarmDescription.setWordWrap(True)
        AlarmDescription.setFixedSize(150, 30)
        AlarmMainLayout.addWidget(AlarmDescription)

        AlarmMainDescription = QLabel(SetupWidget)
        AlarmMainDescription.setText(DescrDict["BreakTimerDesc"]) #rewrite
        AlarmMainDescription.setStyleSheet('padding-left: 2; color: #BFBFBF')
        AlarmMainDescription.setFixedSize(round(SetupWidget.frameGeometry().width()*30/100), 60)
        AlarmMainDescription.setWordWrap(True)
        

        AlarmToggleLayout = QHBoxLayout()

        AlarmMainLayout.addStretch()
        AlarmMainLayout.addWidget(AlarmDescription, alignment=Qt.AlignmentFlag.AlignVCenter)
        AlarmMainLayout.addWidget(AlarmMainDescription)
        AlarmMainLayout.addLayout(AlarmToggleLayout)
        AlarmMainLayout.addStretch()
        

        self.ToggleAlarm = AnimatedToggle(checked_color="#78C1C0", pulse_checked_color="#78C1C0")
        
        self.ToggleAlarm.setFixedSize(70, 60)
        self.ToggleAlarm.setDisabled(True)

        self.OnOffAlarm = QLabel()
    
    
        self.ToggleAlarm.stateChanged.connect(self.AlarmToggleButton)
        self.OnOffAlarm.setFixedSize(50, 50)
        if self.ToggleMain.isChecked():
            self.OnOffAlarm.setStyleSheet('color: black')
        else:
            self.OnOffAlarm.setStyleSheet('color: #AFAFAF')
          
        AlarmToggleLayout.setSpacing(0)
        AlarmToggleLayout.addWidget(self.ToggleAlarm)
        AlarmToggleLayout.addWidget(self.OnOffAlarm)
        AlarmToggleLayout.addStretch()
        
    
    #second part of SetupBox
        self.SecondGroupAlarm(SetupWidget)


    #third part of SetupBox
        
        self.ThirdGroupAlarm(SetupWidget)
       
        SetupBox.addWidget(self.HowOftenBox, alignment=Qt.AlignmentFlag.AlignCenter)
        SetupBox.addWidget(self.BreakBox, alignment=Qt.AlignmentFlag.AlignCenter)


    def SecondGroupAlarm(self, SetupWidget):
        HowOftenLayout = QVBoxLayout()
        self.HowOftenBox = QGroupBox(TitlesDict["HowOftenBoxName"])
        self.HowOftenBox.setLayout(HowOftenLayout)
        self.HowOftenBox.setFixedSize(round(SetupWidget.frameGeometry().width()*31/100), 
                                      round(SetupWidget.frameGeometry().height()*88/100)) 
        
        HowOftenDescription = QLabel(self.HowOftenBox)
        HowOftenDescription.setText(DescrDict["HowOftenDescr"])
        HowOftenDescription.setStyleSheet('color: #BFBFBF')
        HowOftenDescription.setWordWrap(True)

        self.HowOftenSpin = QSpinBox(self.HowOftenBox)
        self.HowOftenSpin.setMinimum(30)
        self.HowOftenSpin.setMaximum(70)
        self.HowOftenSpin.setValue(45)
        self.HowOftenSpin.setFixedSize(140, 32)
        self.HowOftenSpin.setPrefix(DescrDict["EveryPrefix"])
        self.HowOftenSpin.setSuffix(DescrDict["EverySuffix"])
        self.HowOftenSpin.setStyleSheet('''QSpinBox {background-color: white; border: 1px solid; border-color: #B5B4B4; padding-left: 3px}''')


        HowOftenLayout.addWidget(HowOftenDescription, alignment=Qt.AlignmentFlag.AlignTop)
        HowOftenLayout.addWidget(self.HowOftenSpin, alignment=Qt.AlignmentFlag.AlignVCenter)



    def ThirdGroupAlarm(self, SetupWidget):
        BreakLayout = QVBoxLayout()
        self.BreakBox = QGroupBox(TitlesDict["BreakDurationBoxName"])
        self.BreakBox.setLayout(BreakLayout)
        self.BreakBox.setFixedSize(round(SetupWidget.frameGeometry().width()*34/100), 
                                   round(SetupWidget.frameGeometry().height()*88/100))

        BreakDescription = QLabel(self.BreakBox)
        BreakDescription.setText(DescrDict["BreakDurationDescr"])
        BreakDescription.setStyleSheet('color: #BFBFBF')
        BreakDescription.setFixedWidth(round(self.BreakBox.frameGeometry().width()*93/100))
        BreakDescription.setWordWrap(True)



        self.BreakSpin = QSpinBox(self.BreakBox)
        self.BreakSpin.setMinimum(3)
        self.BreakSpin.setMaximum(10)
        self.BreakSpin.setFixedSize(120, 30)
        self.BreakSpin.setSuffix(DescrDict["BreakDurationSuffix"])
        self.BreakSpin.setStyleSheet("QSpinBox {background-color: white; border: 1px solid; border-color: #B5B4B4; padding-left: 3px}")
        

        
        BreakLayout.addWidget(BreakDescription, alignment=Qt.AlignmentFlag.AlignTop)
        BreakLayout.addWidget(self.BreakSpin, alignment=Qt.AlignmentFlag.AlignVCenter)


    def TimerFrameFunc(self):
        self.TimerFrame = QFrame(self.AlarmWidget)
        self.TimerFrame.setFixedSize(round(self.AlarmWidget.frameGeometry().width()*97/100), 
                                round(self.AlarmWidget.frameGeometry().height()*73/100))
        
        TimerFrameLayout = QVBoxLayout(self.TimerFrame)
        self.TimerWiget = QWidget(self.TimerFrame)
        self.TimerWiget.setObjectName('TimerBlock')
        self.TimerWiget.setStyleSheet('''QWidget#TimerBlock {border: 20px solid #F0EEED;
                                                       border-radius: 250px}''')
        
        #TimerWiget was added in order to avoid applying of QFrame styles to all child objects
        #and for adding of the circle arround Timer

        self.TimerWiget.setFixedSize(500, 500)

        self.TimerFrame.setStyleSheet('background-color: #FAFAFA')

        effect = QGraphicsDropShadowEffect(offset=QPoint(2, 2), blurRadius=10, color=QColor("#bdbdbd"))
        self.TimerFrame.setGraphicsEffect(effect)
        
    

        TimerBox = QVBoxLayout(self.TimerWiget)
        self.AlarmSpin = QLabel(self.TimerWiget)
        self.AlarmSpin.setText('00:00:00')
        self.AlarmSpin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.AlarmSpin.setFixedSize(round(self.TimerWiget.frameGeometry().width()*60/100), 
                                round(self.TimerWiget.frameGeometry().height()*40/100))
        font = QFont('', 35, 30, False)
        self.AlarmSpin.setFont(font)

        self.ResetButton = QPushButton(self.TimerWiget)
        self.ResetButton.clicked.connect(self.RessetTimer)
        
        self.ResetButton.setText(ButtonsDict["ResetButton"])
        self.ResetButton.setFixedSize(round(self.TimerWiget.frameGeometry().width()*40/100), 
                                round(self.TimerWiget.frameGeometry().height()*13/100))
        font = QFont('', 13, 2, False)
        self.ResetButton.setFont(font)

        TimerBox.addStretch()   
        TimerBox.addWidget(self.AlarmSpin, alignment=Qt.AlignmentFlag.AlignCenter)
        TimerBox.addWidget(self.ResetButton, alignment=Qt.AlignmentFlag.AlignCenter)
        TimerBox.addStretch()
        
        TimerFrameLayout.addWidget(self.TimerWiget, alignment=Qt.AlignmentFlag.AlignCenter)



    def MainToggleChanged(self, checkQuestion):

        if self.ToggleMain.isChecked():
            self.OnOffMain.setText(ButtonsDict["OnToggle"])
            self.MainTimerLable.setStyleSheet('font-size: 22px; color: black')
            self.ToggleAlarm.setEnabled(True)
            self.OnOffAlarm.setStyleSheet('color: black')
            self.GeneralStopWatchProcess(True)
            self.ToggleMain.setCheckState(2)
                       
        else:
            if checkQuestion:
                qm = QMessageBox()
                resultQ = qm.question(self,TitlesDict["QuestionTitle"], DescrDict["StopMainToolQuestion"], qm.Yes | qm.No)
                StopMainTool = (resultQ == qm.Yes)
            else:
                StopMainTool = True
            if StopMainTool:
                self.OnOffMain.setText(ButtonsDict["OffToggle"])
                self.MainTimerLable.setStyleSheet('font-size: 22px; color: #AFAFAF')
                self.GeneralStopWatchProcess(False)
                if checkQuestion:
                    #self.ToggleAlarm.setDisabled(True)
                    #self.OnOffAlarm.setStyleSheet('color: #AFAFAF')
                    self.DisableAlarm(True)
                self.ToggleMain.setCheckState(0)
                
            else:
                self.ToggleMain.setCheckState(2)


    def UpdateTableContent(self, RunTable):
        if RunTable:
            self.UpdateData(True)

    
    def MainToggleButton(self):
        self.MainToggleChanged(True)

    def GeneralStopWatchProcess(self, isstart):
        ProgressVal = 0
        m.job(True, self.StartValue)
        ActiveState = m.GetActive(False)
        exActiveState = ActiveState

        def StopWatchWork(isstart):
            #return False
            self.MainTimer = QTimer()
            self.MainTimer.timeout.connect(UpdateStopWatchVal)
            if isstart:
                self.MainTimer.start(1000)
            else:
                self.MainTimer.stop()
            
        def UpdateStopWatchVal():
            nonlocal ProgressVal, ActiveState, exActiveState
            exActiveState = ActiveState
            if ActiveState:
                self.StartValue += 1
            ProgressVal += 1
            TimeTuple = GetTimeInFormat(self.StartValue)
            if ProgressVal % cl.CalculateDataDuration == 0:
                OldDates = self.DateList
                OldDate = self.DateChanger.currentText()
                m.job(False, self.StartValue)
                ActiveState = m.GetActive(False)
                #print(ActiveState)
                if exActiveState != ActiveState:
                    self.StartValue = m.SyncTimeTotal()
                    TimeTuple = GetTimeInFormat(self.StartValue)
                NewDates = m.GetDatesList()
                if OldDates != NewDates:
                    self.DateList = NewDates
                    self.DateChanger.clear()
                    self.DateChanger.addItems(self.DateList)
                    if OldDate in NewDates:
                        self.DateChanger.setCurrentText(OldDate)
                    else:
                        self.DateChanger.setCurrentText(self.DateList[0])
                    self.StartValue = m.GetStartTime()
                    TimeTuple = GetTimeInFormat(self.StartValue)

                if self.DateChanger.currentText() == self.DateList[0]:
                    self.UpdateData(False)
            self.MainTimerLable.setText('{:0>2}:{:0>2}:{:0>2}'.format(*TimeTuple))
        
        StopWatchWork(isstart)

    
    def AlarmToggleButton(self):
        self.AlarmToggleChanged(True)
        
    
    def AlarmToggleChanged(self, checkQuestion):

        if self.ToggleAlarm.isChecked():
            self.OnOffAlarm.setText(ButtonsDict["OnToggle"])
            self.BreakBox.setEnabled(True)
            self.HowOftenBox.setEnabled(True)
            self.BreakBox.setStyleSheet('color: black')
            self.HowOftenBox.setStyleSheet('color: black') 
            self.TimerWiget.setEnabled(True)
            self.ResetButton.setStyleSheet("QPushButton {border: 1px solid #F0EEED; border-radius: 10px; background-color: #78C1C0; font-size: 30px; color: white}"
                                "QPushButton:pressed {background-color: #F0EEED; border: 1px solid #F0EEED; border-radius: 10px}")
            self.AlarmSpin.setStyleSheet('color: #515151')
            self.GeneralTimerProcess(True)
            self.ToggleAlarm.setCheckState(2)
        else:
            StopAlarmTool = self.GlobalStop
            if (checkQuestion) and (not StopAlarmTool):
                qm = QMessageBox()
                resultQ = qm.question(self,TitlesDict["QuestionTitle"], DescrDict["StopAlarmToolQuestion"], qm.Yes | qm.No)
                StopAlarmTool = (resultQ == qm.Yes)
            else:
                StopAlarmTool = True
            if StopAlarmTool:
                self.DisableAlarm(False)
            else:
                self.ToggleAlarm.setCheckState(2)



    def DisableAlarm(self, GlobalStopVal):
        self.OnOffAlarm.setText(ButtonsDict["OffToggle"]) 
        self.BreakBox.setDisabled(True)
        self.HowOftenBox.setDisabled(True)
        self.HowOftenBox.setStyleSheet('color: #AFAFAF')
        self.BreakBox.setStyleSheet('color: #AFAFAF')
        self.ResetButton.setStyleSheet("QPushButton {border: 1px solid #F0EEED; border-radius: 10px; background-color: #F0EEED; color: #AFAFAF}")
        self.TimerWiget.setDisabled(True)
        self.AlarmSpin.setStyleSheet('color: #AFAFAF')
        self.GeneralTimerProcess(False)
        self.AlarmSpin.setText('00:00:00')
        self.GlobalStop = GlobalStopVal
        self.ToggleAlarm.setCheckState(False)

                

    def GeneralTimerProcess(self, isstart): 
        UserGoOut = False  #shows that a user stopped working 
        if isstart:                           
            FinalValue = self.HowOftenSpin.value()*60    #shows initial time
        else:
            FinalValue = 0
        ReverseTimerVal = 0             #for reversal time calculation
        CheckingStatus = False          #for 1 min which we give to go to break after 45 min working
        SetZeroTimer = False

                   
        def TimerWork(isstart):
            self.TimerAlarm = QTimer()
            self.TimerAlarm.timeout.connect(UpdateTimerFunc)
            if isstart:
                self.TimerAlarm.start(1000)
            else:
                self.TimerAlarm.stop()

        

        def UpdateTimerFunc():

            def SetZeroTimerValues():
                #2 cases: user does not work and user stopped working
                nonlocal FinalValue, ReverseTimerVal, CheckingStatus, UserGoOut, SetZeroTimer
                FinalValue = 0
                ReverseTimerVal = 0
                CheckingStatus = False
                UserGoOut = True
                self.UpdateTimerVal(not CheckingStatus, FinalValue)


            nonlocal FinalValue, ReverseTimerVal, CheckingStatus, UserGoOut, SetZeroTimer
            UserIsActive, LongAbsence = m.GetActive(True)
            if (LongAbsence)&(UserIsActive):
                self.GeneralTimerProcess(True) #start from very beginning


            """ print('UserIsActive - ', UserIsActive,
                'CheckingStatus - ', CheckingStatus,
                    'UserGoOut - ', UserGoOut,
                    'LongAbsence - ', LongAbsence,
                    'ReverseTimerVal - ', ReverseTimerVal,
                    'SetZeroTimer - ', SetZeroTimer,
                    'FinalValue - ', FinalValue) """
                      
            if FinalValue > 0:
                FinalValue -= 1
                self.UpdateTimerVal(not CheckingStatus, FinalValue)

                if not UserIsActive:
                    SetZeroTimer = (CheckingStatus)| ((ReverseTimerVal > self.BreakSpin.value()*60) & (UserGoOut))
                    #if a user stopped working after 45 min or in the middle of 45 min 

                    if SetZeroTimer:
                        SetZeroTimerValues()
                    else:
                        if not UserGoOut: #user stopped working but is not active < 3 min only
                            UserGoOut = True
                            ReverseTimerVal = 1
                        else: 
                            ReverseTimerVal += 1
                else:
                    ReverseTimerVal = 0 #user backed to work earlier than 45 min finished
                    UserGoOut = False

            else:  #time finished
                """ print('run alarm', 'UserIsActive - ', UserIsActive,
                'CheckingStatus - ', CheckingStatus,
                    'UserGoOut - ', UserGoOut,
                    'LongAbsence - ', LongAbsence,
                    'ReverseTimerVal - ', ReverseTimerVal,
                    'SetZeroTimer - ', SetZeroTimer,
                    'FinalValue - ', FinalValue) """
                
                if (not SetZeroTimer)&(not CheckingStatus):   #if user worked before this time and it is not checking
                    AB = AlarmMsgBox()                
                    if AB.RunAlarmWindow():                     #user clicked 'Notify in 3 min'
                        FinalValue = cl.NotifyAfterTime*60
                    else:                                       #user clicked OK
                        FinalValue = cl.CheckingTime*60
                        CheckingStatus = True           #we give 1 min to user to go to break otherwise start again
                                        
                else:                                           #user did not work before this time
                    if UserIsActive:
                        self.GeneralTimerProcess(True)
                    else:
                        SetZeroTimerValues()


         
        TimerWork(isstart)


    def RessetTimer(self):
        qm = QMessageBox()
        resultQ = qm.question(self,TitlesDict["QuestionTitle"], DescrDict["QuestionTitleDescr"], qm.Yes | qm.No)
        if resultQ == qm.Yes:
            self.AlarmSpin.setText('00:00:00')
            self.FinalValue = self.HowOftenSpin.value()*60
            self.GeneralTimerProcess(True)
   

    def UpdateTimerVal(self, ShowTimer, TimeToShow):       
        if ShowTimer:
            TimeTuple = GetTimeInFormat(TimeToShow)
            self.AlarmSpin.setText('{:0>2}:{:0>2}:{:0>2}'.format(*TimeTuple))
        else:
            TimeTuple = GetTimeInFormat(0)
            self.AlarmSpin.setText('{:0>2}:{:0>2}:{:0>2}'.format(*TimeTuple))



    def closeEvent(self, QCloseEvent):
        #Window should go to tray
        self.trayW.show()
        QCloseEvent.ignore()
        self.hide()

    def activateW(self, reason):
        #running from tray
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()
        else:
            self.destroy()

    def quitTimer(self):
        self.GeneralStopWatchProcess(False)
        QApplication.quit()
        

        
def GetTimeInFormat(TimeSec):
        h, s = divmod(TimeSec, 3600)
        m, s = divmod(s, 60)
        return (int(h), int(m), int(s))

def run_app():
    form = QApplication(sys.argv)
    form.setQuitOnLastWindowClosed(False)
    WidMain = TimeMgtApp()
    WidMain.show()
    form.exec_()
    


if __name__== '__main__':

    #if not ctypes.windll.shell32.IsUserAnAdmin():
    #    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    
    run_app()
    

    

    """ form = QApplication(sys.argv)
    f = AlarmMsgBox()
    f.RunAlarmWindow() """



