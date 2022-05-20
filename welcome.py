import sys
import re
import math
from pytube import YouTube , Playlist , Channel
import requests
from PyQt5 import QtCore 
from PyQt5.QtGui import QImage , QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog , QApplication , QWidget , QStackedWidget , QMainWindow

class WelcomeScreen(QDialog):
    
    def __init__(self):
        super(WelcomeScreen , self).__init__()
        loadUi('firstScreen.ui' , self)

        self.initGUI()
    
    def initGUI(self):
        self.linkBtn.clicked.connect(self.goToDownload)
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
    
    def goToDownload(self):

        link = self.lineEdit.text()

        if len(link) != 0:
            screen = DownloadScreen(link)
            stack.addWidget(screen)
            stack.setCurrentIndex(stack.currentIndex() + 1)
        # screen.show()

class DownloadScreen(QDialog):
    
    def __init__(self , link):
        super(DownloadScreen , self).__init__()

        self.link = link

        loadUi('downloadScreen.ui' , self)
        self.type = self.getType()


    
    def getType(self):

        if 'watch' in self.link.lower():
            return self.getVideoInfo()
        elif 'playlist' in self.link.lower():
            return self.getPlayListInfo()
        elif 'channel' in self.link.lower():
            return 2
        else: 
            return 3

    def getPlayListInfo(self):
        
        try:
            playList = Playlist(self.link)
            self.listGUI(playList)
        except:
            print('invalid playlist')
            
        

    def listGUI(self , playlist):


        yt = YouTube(playlist[0])

        title = playlist.title
        imageUrl = yt.thumbnail_url

        self.comboBox.setVisible(False)

        

        self.progressBar.setValue(0)




        image = QImage()
        image.loadFromData(requests.get(imageUrl).content)
        self.name.setText(title)
        self.image.setPixmap(QPixmap(image))
        self.image.setScaledContents(True)


        self.downloadBtn.clicked.connect(lambda : self.downloadOneVideo(playlist))



    def downloadOneVideo(self , playlist):

        for video in playlist:

            yt = YouTube(video,
            on_progress_callback = self.updateProgressBar,
            on_complete_callback = self.completed
            )

            self.updateGUIforAVideo(yt)

    
    def updateGUIforAVideo (self , yt):

        title = yt.title
        imageUrl = yt.thumbnail_url

        self.progressBar.setValue(0)



        image = QImage()
        image.loadFromData(requests.get(imageUrl).content)
        self.name.setText(title)
        self.image.setPixmap(QPixmap(image))
        self.image.setScaledContents(True)




        

    


    

    def getVideoInfo(self):
        
        isValid , yt = self.validateVideo()

        if isValid:
            self.updateGUI(yt)


    def updateGUI(self , yt):
        
        title = yt.title
        imageUrl = yt.thumbnail_url

        self.progressBar.setValue(0)



        image = QImage()
        image.loadFromData(requests.get(imageUrl).content)
        self.name.setText(title)
        self.image.setPixmap(QPixmap(image))
        self.image.setScaledContents(True)

        self.downloadBtn.clicked.connect(lambda : self.download(yt))

        self.addQualities(yt)

    
    def download(self , yt):

        itag = self.dict[self.comboBox.currentText()]

        stream = yt.streams.get_by_itag(itag)

        stream.download()
    
    def addQualities(self ,yt):

        
        videoFilters = yt.streams

        self.dict = {}

        regex = r"\d+p"

        for video in videoFilters:
            
            regexMatch = re.findall(regex , str(video))
            if regexMatch:
                self.dict[regexMatch[0] + "   " +video.mime_type] = int(video.itag)
                self.comboBox.addItem(regexMatch[0] + "   " +video.mime_type)


    def updateProgressBar(self , stream , chunk , bytes_remaining):
        
        size = stream.filesize

        self.progressBar.setValue(60)

    # def percent(self, tem, total):
    #     perc = (float(tem) / float(total)) * float(100)
    #     return math.ceil(perc)
        
    def completed(self , stream , filePath):
        self.progressBar.setValue(100)
        print(filePath)

    def validateVideo(self):
        
        try : 
            yt = YouTube(self.link,
            on_progress_callback = self.updateProgressBar,
            on_complete_callback = self.completed
            )
            return True , yt
        except:
            print('Not Valid Name')
            return False , None


# https://www.youtube.com/watch?v=Oa7LYZHm7wU

app = QApplication(sys.argv)
screen = WelcomeScreen()
screen.setFixedSize(1200 , 800)

stack = QStackedWidget()
stack.addWidget(screen)
stack.setFixedSize(1200 , 800)
stack.show()

sys.exit(app.exec_())
