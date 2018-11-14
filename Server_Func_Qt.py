# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 15:39:31 2018

@author: UNICOMNET
"""

import socket
import threading as thread
import PyQt5.QtCore as core
import PyQt5.QtGui as gui
import traceback
from time import sleep
connlist = [] #연결된 클라이언트 정보 저장할 리스트
namelist = [] #표시할 닉네임 리스트
addrlist = [] #클라이언트 재연결을 위한 아이피(포트)리스트
#HOST = 'localhost'
#PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #소켓 생성
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #소켓 옵션, 재사용

def excute_func(conn, addr, chatBrowser):
    
    client_ID = conn.recv(1024)#연결 후 첫 입력은 닉네임
    client_ID = client_ID.decode()
    if client_ID in namelist:#중복 닉네임 
        conn.send(toSpanText("중복된 닉네임이있습니다.").encode("utf-8"))
        conn.close()
        connlist.remove(conn)
        return
    namelist.append(client_ID)#리스트에 추가
    userlistview.addItem(client_ID)#뷰에 이름 추가
    echo(client_ID+" 접속", conn)#클라이언트에게 접속메세지
    chatBrowser.append(client_ID+" 접속")
    chatBrowser.moveCursor(gui.QTextCursor.End)
    new_user(client_ID, conn)#다른 유저들에게 이 유저의 입장을 알림
    send_userlist(conn)#첫 전송메세지는 현재 유저의 리스트
    
    
    while 1:
        try:
            if conn._closed:
                return
            message = conn.recv(1024)
            message = message.decode()
            
            if not message:#check if EOF
                print("eof")
                connlist.remove(conn)
                namelist.remove(client_ID)
                conn.close()
                chatBrowser.append(toSpanText(client_ID+" has disconnected"))
                chatBrowser.moveCursor(gui.QTextCursor.End)
                break
            elif not message.find(":whisper") == -1:
                print("whisper")
                whisper(message.split(":whisper")[0],message.split(":whisper")[1], client_ID, chatBrowser)
                continue
            elif message in ['Client Quit']:#연결종료문자가 오면, 
                print("quit")
                connlist.remove(conn)
                conn.close()#연결 종료
                chatBrowser.append(toSpanText(client_ID+" has disconnected"))
                chatBrowser.moveCursor(gui.QTextCursor.End)
                echo(client_ID+" has disconected")#퇴장을 알림
                gone_user(client_ID)
                
                items = userlistview.findItems(client_ID, core.Qt.MatchExactly)
                if len(items) > 0:#유저리스트뷰에서 제거
                    for item in items:
                        row = userlistview.row(item)
                        userlistview.takeItem(row)
                namelist.remove(client_ID)
                
                break  
                
            else:#종료가 아니면
                print("msg")
                echo_msg = client_ID+" :: "+message
                chatBrowser.append(client_ID+" :: "+message)
                
                echo(echo_msg, conn)#모든 연결에 메세지 뿌림
           
        except:
            print("exc")
            sleep(0.1)
            if not s._closed:
                print("exc1")
                connlist.remove(conn)
                echo(client_ID+" has disconected")
                chatBrowser.append(toSpanText(client_ID+" has disconnected"))
                chatBrowser.moveCursor(gui.QTextCursor.End)
                gone_user(client_ID)
                items = userlistview.findItems(client_ID, core.Qt.MatchExactly)
                if len(items) > 0:#유저리스트뷰에서 제거
                    for item in items:
                        row = userlistview.row(item)
                        userlistview.takeItem(row)
                namelist.remove(client_ID)
                print("exc2")
            break;
            
        chatBrowser.moveCursor(gui.QTextCursor.End)
    return
    


def echo(message, Caller = None):
    for conn in connlist:
        try:
            if not Caller is conn:
                
                conn.send(toSpanText(message).encode("utf-8"))
        except:
            pass
#            connlist.remove(conn)
    return

def whisper(message, target, sender, chatBrowser):
    try:
        idx = namelist.index(target)
    except:
        return
    if idx == -1:
        return
    if idx == 0:
        chatBrowser.append(sender+"님의 귓속말 : "+message)
        chatBrowser.moveCursor(gui.QTextCursor.End)
        return
    wMessage = sender+"님의 귓속말 : "+message 
    connlist[idx-1].send(wMessage.encode("utf-8"))
    return

def toSpanText(message):
    return "<span style=\"color:#000000\">"+message+"</span>"

def input_message(message, chatBrowser, nickname, color,  target, ischecked):
    message = "<span style=\"color:"+color.name()+"\">"+message+"</span>"
    if ischecked and not target is "" :
        chatBrowser.append(target+"에게 :: "+message)
#        message = message +":whisper"+target
        whisper(message, target, nickname, chatBrowser)
    else:
        chatBrowser.append("Me :: "+message)
        message = nickname+" :: "+message
        echo(message)
    
    chatBrowser.moveCursor(gui.QTextCursor.End)
    
def auto_connector(chatBrowser):
    while True:
        try:
            conn, addr = s.accept()
            thread._start_new_thread(excute_func,(conn, addr, chatBrowser))
            connlist.append(conn)
            addrlist.append(int(addr[1]))
        except:
            break
            
    return

def send_userlist(conn):
    for user in namelist:
        msg = user+":user"
        sleep(0.01)
        conn.send(msg.encode("utf-8"))

def new_user(name, Caller = None):
    for conn in connlist:
        if not Caller is conn:
            msg = name+":user"
            
            conn.send(msg.encode("utf-8"))

def gone_user(name):
    
    for conn in connlist:
        
        msg = name+":gone"
        conn.send(msg.encode("utf-8"))


def shutdown(chatBrowser):
#    print("shutdown")
    if not s._closed:
            
        echo('서버 사용자에 의해 종료됩니다.')
        chatBrowser.append("종료합니다.")
        userlistview.clear()
        for conn in connlist:
            data = str(addrlist)+":addrlist"
            conn.send(data.encode("utf-8"))
        
        for conn in connlist:
    #        data = str(addrlist)+":addrlist"
    #        conn.send(data.encode("utf-8"))
            conn.shutdown(socket.SHUT_WR)
            conn.close()
    #    connlist.clear()
        s.close()
    return


def boot_Server(chatBrowser, app, userlist, nickname):
    
    global window, userlistview
    userlistview = userlist
    
    connlist.clear()
    addrlist.clear()
    namelist.clear()
    namelist.append(nickname)
    userlistview.addItem(nickname)
    window = app
    s.bind(('localhost', 1234)) 
    s.listen(0) #클라이언트의 연결 대기
    chatBrowser.append("호스트입니다.")
    chatBrowser.moveCursor(gui.QTextCursor.End)
    thread._start_new_thread(auto_connector,(chatBrowser, ))
#    print('클라이언트에게 보낼 내용 입력 가능')
#    while True:
#        myMessage = input()
#        if myMessage in ['quit','Quit','QUIT']:
#            shutdown()
#            break
#        myMessage = "from Server :: "+myMessage
#        echo(myMessage)
