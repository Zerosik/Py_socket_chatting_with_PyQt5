# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:42:03 2018

@author: UNICOMNET
"""

import socket
import threading as thread
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import traceback
HOST = 'localhost'
PORT = 1234
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

data = ''
nextHost = False
def get_msg(chatBrowser):
    tp = None
    
    while True:
        try:
            message = s.recv(1024)
            message = message.decode()
            if not message.find(":user") == -1:
                userlistview.addItem(message.split(":user")[0])

                continue
            elif not message.find(":gone") == -1:
                goneuser = message.split(":gone")[0]
                items = userlistview.findItems(goneuser, core.Qt.MatchExactly)
                if len(items) > 0:
                    for item in items:
                        row = userlistview.row(item)
                        userlistview.takeItem(row)
                continue
            elif not message.find(":addrlist") == -1:
                
                
                value = message.split(":addrlist")[0]
                addrlist = eval(value)
                minaddr = 99999
                for addr in addrlist:
                    if minaddr>addr:
                        minaddr = addr
                myaddr = s.getsockname()
                if minaddr == myaddr[1]:
                    tp = True
                else:
                    tp =  False
            elif not message:
#                chatBrowser.append(toSpanText("연결 종료됨"))
#                nicknameEdit.setEnabled(True)
#                connBtn.setEnabled(True)
                userlistview.clear()
                s.close()
                return tp
#            elif message in ['!!!server shutdown immediately!!!']:
#                chatBrowser.append(toSpanText('종료됨'))
#                s.shutdown(socket.SHUT_RD)
#                s.close()
#                return
            else:
                chatBrowser.append(message)
            chatBrowser.moveCursor(gui.QTextCursor.End)
        except:
            traceback.print_exc()
            chatBrowser.append(toSpanText('서버 강제종료됨'))
            chatBrowser.moveCursor(gui.QTextCursor.End)
            userlistview.clear()
            nicknameEdit.setEnabled(True)
            connBtn.setEnabled(True)
            s.close()
            return None
        

def toSpanText(message):
    return "<span style=\"color:#000000\">"+message+"</span>"

def input_message(message, chatBrowser, color, target, ischecked):
#    originText = label["text"]
#    label.config(text = originText+"\n"+message)
    message = "<span style=\"color:"+color.name()+"\">"+message+"</span>"
    if ischecked and not target is "" :
        chatBrowser.append(target+"에게 :: "+message)
        message = message +":whisper"+target
        print(message)
    else:
        chatBrowser.append("Me :: "+message)
    if s._closed:
        return
    message = message.encode("utf-8")   # byte형으로 변환하기 위해
    s.send(message)
    chatBrowser.moveCursor(gui.QTextCursor.End)
    
def close_socket(chatBrowser):
    if not s._closed:
        s.send('Client Quit'.encode("utf-8"))
        chatBrowser.append("연결 종료합니다.")
        chatBrowser.moveCursor(gui.QTextCursor.End)
        s.close()
    return
    
def set_id(Id):
    s.send(Id.encode("utf-8"))
    
    
def boot_Client(chatBrowser, nickname, userlist, nameEdit, conBtn):
    global userlistview, nicknameEdit, connBtn
    
    connBtn = conBtn
    userlistview = userlist
    nicknameEdit = nameEdit
    nicknameEdit.setEnabled(False)
    connBtn.setEnabled(False)
    try:
        s.settimeout(10)
        s.connect((HOST, PORT))
        s.settimeout(None)
        chatBrowser.append("연결되었습니다.")
        chatBrowser.moveCursor(gui.QTextCursor.End)
    except:
        s.close()
        chatBrowser.append("서버를 찾지 못했습니다.")
        chatBrowser.moveCursor(gui.QTextCursor.End)
        return False
#    print('enter your id')
#    my_ID = input()
#    s.send(my_ID.encode("utf-8"))
    s.send(nickname.encode("utf-8"))
#    thread._start_new_thread(get_msg,(chatBrowser,))
    return True
#    while 1:
#        send_data = input()
#        
#        # 파이썬3 에서는 아래서 사용할 send() 메소드가 str형을 지원하지 않는다.
#        # 실제로 파이썬2 에서는 위의 encoding 과정이 생략되어도 함수 사용에 문제가 없음.
#
#        if send_data in ['quit', 'Quit', 'QUIT']:
#            s.send('Client Quit'.encode("utf-8"))
#            s.close()
#            break;
#        if s._closed:
#            break;
#        send_data = send_data.encode("utf-8")   # byte형으로 변환하기 위해
#        s.send(send_data)   # 실제 오류가 발생하는 부분