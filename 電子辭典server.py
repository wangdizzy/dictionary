import socket
import sys
import os
import signal
import time
import pymysql

dict_txt = '/media/sf_Ubuntushare/dict.txt'


HOST = '172.16.0.106'
PORT = 7778
ADDR = (HOST,PORT)


#並發連接請求
def main():
	db = pymysql.connect('localhost','root','a123456','dict')

	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(ADDR)
	s.listen(5)

	signal.signal(signal.SIGCHLD,signal.SIG_IGN)

	while True:
		try:
			user,addr = s.accept()
			print('user from',addr)
		except KeyboardInterrupt:
			os._exit(0)
		except:
			continue

		pid = os.fork()
		if pid < 0:
			print('失敗')
			user.close()
		elif pid == 0:
			s.close()
			do_child(user,db)
		else:
			user.close()
			continue
	
	db.close()
	s.close()
	os._exit(0)

#執行子進程具體任務
def do_child(user,db):
	while True:
		data = user.recv(128).decode()
		print('Register:',data)
		if data[0] == 'R':
			do_register(user,data,db)
		elif data[0] == 'L':
			do_login(user,data,db)
		elif data[0] == 'Q':
			do_quit(user)
		elif data[0] == 'S':
			do_query(user,data,db)
		elif data[0] == 'H':
			do_history(user,data,db)

#註冊
def do_register(user,data,db):
	print('執行註冊')
	cursor = db.cursor()
	L = data.split(' ')
	user_name = L[1]
	passwd = L[2]
	
	sql = 'select * from user where name = "%s"'%user_name
	cursor.execute(sql)
	r = cursor.fetchone()
	
	if r != None:
		user.send('用戶存在'.encode())
		return
	
	sql = 'insert into user values("%s","%s")'%(user_name,passwd)
	try:
		cursor.execute(sql)
		db.commit()
		user.send("OK".encode())
	except:
		use.send('Fall'.encode())
		db.rollback()
		return
	else:
		print('註冊成功')


#斷開連結結束子進程
def do_quit(user):
	user.close()
	sys.exit(0)

#登入
def do_login(user,data,db):
	print('登入操作')
	cursor = db.cursor()
	L = data.split(' ')
	name = L[1]
	passwd = L[2]

	try:
		sql = 'select * from user where name="%s" and passwd="%s"'%(name,passwd)
		cursor.execute(sql)
		r = cursor.fetchone()
	except:
		pass
	if r == None:
		user.send('Fall'.encode())
	else:
		user.send('OK'.encode())

#查詢
def do_query(user,data,db):
	print('查詢操作')
	cursor = db.cursor()
	L = data.split(' ')
	name = L[1]
	word = L[2]

	try:
		f = open(dict_txt,'rb')
		user.send('OK'.encode())
	except:
		user.send('Fall'.encode())
		return
	time.sleep(0.1) #防止沾包
	while True:
		line = f.readline().decode()
		tmp = line.split(' ')
		if word == tmp[0]:
			user.send(line.encode())
			insert_history(name,word,db)
			f.close()
			return
		elif word < tmp[0]:
			user.send('not found'.encode())
			f.close()
			break
	return

#插入歷史紀錄
def insert_history(name,word,db):
	print('插入記錄')
	cursor = db.cursor()
	sql = 'insert into hist value ("%s","%s","%s")'%(name,time.ctime(),word)
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
		return
	else:
		print('插入成功')

#查看歷史紀錄
def do_history(user,data,db):
	print('查看操作')
	name = data.split(' ')[1]
	
	cursor = db.cursor()

	try:
		sql = 'select * from hist where name="%s"'%(name)
		cursor.execute(sql)
		r = cursor.fetchall()
		if not r:
			user.send('Fall'.encode())
		else:
			user.send('OK'.encode())
	except:
		pass
	for i in r:
		time.sleep(0.1)
		msg = ('%s查詢單字%s在：%s')%(i[0],i[2],i[1])
		user.send(msg.encode())
	time.sleep(0.1)
	user.send('##'.encode())

if __name__ =='__main__':
	main()