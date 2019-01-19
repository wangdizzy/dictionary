import socket
import sys
import os
import signal
import time
import pymysql


#發送連接請求
def main():
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    
    s = socket.socket()
    s.connect((HOST,PORT))

    while True:
        print('''
            ============歡迎使用============
            |   1.註冊   2.登入   3.退出   |
            ================================
            ''')
        try:
            cmd = int(input('輸入選項：'))
        except:
            print('請請入1,2,3其中一個')
            continue
        if cmd not in [1,2,3]:
            print('輸入有誤')
            sys.stdin.flush()#清空緩存
            continue
       
        if cmd == 1:
            if do_register(s) == 0:
                print('註冊成功')
            else:
                print('註冊失敗')
        elif cmd == 2:
            name = do_login(s)
            if name == -1:
                print('登入失敗')
            else:
                print('登入成功')
                login(s,name)
        elif cmd == 3:
            do_quit(s)
            


#發送註冊請求
def do_register(s):
    while True:
        name = input('用戶名：')
        passwd = input('密碼：')
        passwd1 = input('重新輸入密碼：')
        if passwd != passwd1:
            print('密碼不一致')
            continue
        msg = 'R %s %s'%(name,passwd)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            return 0
        elif data == 'Fall':
            print('用戶名存在')
            return -1
        else:
            return -1


#用戶退出
def do_quit(s):
    s.send('Q'.encode())
    s.close()
    sys.exit(0)

#二級界面
def login(s,name):
    while True:
        print('''
        ============歡迎使用==============
        |  1.查單字  2.歷史紀錄  3.退出  |
        ==================================
        ''')
        try:
            cmd = int(input('輸入選項：'))
        except:
            print('請請入1,2,3其中一個')
            continue
        if cmd not in [1, 2,3]:
            print('輸入有誤')
            sys.stdin.flush()  # 清空緩存
            continue

        if cmd == 1:
            do_query(s,name)
        elif cmd == 2:
            do_history(s,name)
        elif cmd == 3:
            break

#登入請求
def do_login(s):
    name = input('輸入用戶名：')
    passwd = input('輸入密碼：')

    msg = 'L %s %s'%(name,passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        return name
    else:
        return -1

#循環發送查詢請求
def do_query(s,name):
    while True:
        word = input('查詢單字：')
        if word == '#':
            break
        msg = 'S %s %s'%(name,word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            if data == 'not found':
                print('無此單字解釋')
            else:
                print(data)
        else:
            print('失敗')

#發送查看紀錄請求
def do_history(s,name):
    msg = 'H %s'%(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print('查看失敗')

   

if __name__ =='__main__':
    main()