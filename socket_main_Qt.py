# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 15:48:39 2018

@author: UNICOMNET
"""

import sys
import PyQt5.QtWidgets as QtWidget
import PyQt5.QtGui as QtGui
import PyQt5.uic as uic
from importlib import reload
import threading as thread
#from PyQt5.QtCore import pyqtSlot
import atexit
import time
#시작버튼 conBtn, QPushButton
#종료버튼 quitBtn, QPushButton
#채팅박스 textBrowser, QTextBrowser
#유저정보 userList, QListWidget
#전송버튼 sendBtn, QPushButton
#입력상자 sendText, QLineEdit
#닉네임 nicknameEdit, QLineEdit
#색상버튼 colorBtn , QPushButton
#귓속말체크 whisperCheck, QCheckBox


form_class = uic.loadUiType("socket_Qt_UI.ui")[0]

class MyWindow(QtWidget.QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        global nameEdit, connBtn
        self.setupUi(self)
        self.conBtn.clicked.connect(self.__Start)
#        self.quitBtn.clicked.connect(app.quit)
        self.colorBtn.clicked.connect(self.colorBtnClick)
        self.userList.itemClicked.connect(self.user_clicked)
        
        
    def user_clicked(self, item):
        global target
        nick = self.nicknameEdit.text()
        tg = item.text()
        if nick == tg:
            target = ""
        else:
            target = item.text()
        
#    def Start_Server(self):
#        
#        def sendMessage():
#            if sv.s._closed:
#                app.quit()
#            else:
#                sv.input_message(self.sendText.text(), self.textBrowser)
#                self.sendText.setText("")
#        
#        self.textBrowser.append("서버 실행합니다.")
#        import Server_Func_Qt as sv#load moduled
#        sv.boot_Server(self.textBrowser, app)
#        self.sendText.returnPressed.connect(sendMessage)
#        self.sendBtn.clicked.connect(sendMessage)
#        
#        pass
#    @pyqtSlot()
    def colorBtnClick(self):
        openColorDialog(self)
        
        
    def disconnectFunc(self, obj):
        while True:
            try:
                obj.clicked.disconnect()
            except:
                break
            
    def __Start(self):
        global sType#false = client, true = server
        global isinit
        
        def sendMessage():
            if not sType:
                sv_sendMessage()
            else:
                cl_sendMessage()
        
        def cl_sendMessage():
#            print("clsend")
            global color, target
#            print(cl.s._closed)
            if cl.s._closed:
                target = ""
                self.__Start()
#                app.quit()
            else:
                if not self.sendText.text() is "":
                    cl.input_message(self.sendText.text(), self.textBrowser, color, target, self.whisperCheckBox.isChecked())
                    self.sendText.setText("")
#                    print(self.sendText.text()+""+target+""+str(self.whisperCheckBox.isChecked()))
                pass
            
            
        def sv_sendMessage():
#            print(sv.s._closed)
#            print("svsend")
            if sv.s._closed:
                self.__Start()
#                app.quit()
            else:
                if not self.sendText.text() is "":
                    sv.input_message(self.sendText.text(), self.textBrowser, self.nicknameEdit.text(), color, target, self.whisperCheckBox.isChecked())
                    self.sendText.setText("")
                pass
        
        
        def event_disconnector():
            self.disconnectFunc(self.sendBtn)
            self.disconnectFunc(self.quitBtn)
            self.sendText.returnPressed.disconnect()
            self.quitBtn.clicked.connect(app.quit)
        
        def quit_event():
            self.nicknameEdit.setEnabled(True)
            self.conBtn.setEnabled(True)
            
            if not sType:
                print("server quit")
                sv.shutdown(self.textBrowser)
            else:
                print("client quit")
                cl.close_socket(self.textBrowser)
        
        
        def event_setter():
                self.sendText.returnPressed.connect(sendMessage)
                self.sendBtn.clicked.connect(sendMessage)
                self.quitBtn.clicked.connect(quit_event)
        
        def Restarter(cl):
            
            global target
            from multiprocessing.pool import ThreadPool
            pool = ThreadPool(processes=1)
            
            async_result = pool.apply_async(cl.get_msg, (self.textBrowser,)) # tuple of args for foo
            
            # do some other stuff in the main process
            
            return_val = async_result.get()  # get the return value from your function.
            
            time.sleep(0.5)
    
            if return_val is None:
                print("pass")
            elif return_val:#if restart with server
                self.textBrowser.append("재연결 시도합니다.")
#                print(cl.s._closed)
                cl_sendMessage()
#                event_setter(False)
                pass
            else:
                self.textBrowser.append("재연결 시도합니다.")
#                print(cl.s._closed)
                time.sleep(0.5)
                cl_sendMessage()
#                event_setter(True)
                pass
            return
        
#################MAIN##############
        if self.nicknameEdit.text() is "":
            QtWidget.QMessageBox.about(self, "Alert", "닉네임을 입력하세요")
            
        else:
            if not isinit:
                event_setter()
                print("eventInit")
                isinit = True
            import Client_Func_Qt as cl
            import Server_Func_Qt as sv
            reload(cl)
            if cl.boot_Client(self.textBrowser, self.nicknameEdit.text(), self.userList, self.nicknameEdit, self.conBtn):#When Client
#                atexit.register(cl.s.close)
                thread._start_new_thread(Restarter, (cl, ))
                sType = True
                print("boot_Client")
            else:#When server
                reload(cl)
                reload(sv)
                sv.boot_Server(self.textBrowser, app, self.userList, self.nicknameEdit.text())
                time.sleep(1)
#                atexit.register(sv.s.close)
                sType = False
                print("boot_Client")
        

def openColorDialog(self):
    global color
    color = QtWidget.QColorDialog.getColor()
        
if __name__ == "__main__":
    global app, color, target
    global isinit
    isinit = False
    target = ""
    color = QtGui.QColor()
    app = QtWidget.QApplication(sys.argv)
    myWindow = MyWindow() 
    myWindow.show()
    app.exec_()