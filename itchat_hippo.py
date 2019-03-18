#!/usr/bin/python
# -*-coding:utf-8 -*-

import itchat
from itchat.content import TEXT
from itchat.content import *
import sys
import re
import os
import json

#from flask import Flask, render_template, url_for, request,redirect,make_response,session,flash,abort,Response
#from flask import send_file
#from flask import send_from_directory

itchat.auto_login(hotReload=True,enableCmdQR=False)
chatroom_list={}


#app = Flask(__name__)
#app.secret_key='this is xiaonan home'

# 这里的TEXT表示如果有人发送文本消息()
# TEXT    文本    文本内容(文字消息)
# MAP    地图    位置文本(位置分享)
# CARD    名片    推荐人字典(推荐人的名片)
# SHARING    分享    分享名称(分享的音乐或者文章等)
# PICTURE 下载方法        图片/表情
# RECORDING    语音    下载方法
# ATTACHMENT    附件    下载方法
# VIDEO    小视频    下载方法
# FRIENDS    好友邀请    添加好友所需参数
# SYSTEM    系统消息    更新内容的用户或群聊的UserName组成的列表
# NOTE    通知    通知文本(消息撤回等)，那么就会调用下面的方法


'''
@app.route('/', methods=['GET'])
def index():
	abort(404)
'''


def myupdate_chatroom(cr_list,UserName,NickName,MemberCount,MemberList):
	if UserName in cr_list:
		if cr_list[UserName]['NickName'] == '':
			cr_list[UserName]['NickName'] = NickName
		if MemberCount != 0:
			cr_list[UserName]['MemberCount'] = MemberCount
	else:
		memlist={}
		cr_list[UserName] = {'NickName':NickName,'MemberCount':MemberCount,'MemberList':memlist}

	if len(cr_list[UserName]['MemberList']) != cr_list[UserName]['MemberCount']:
		print("成员人数不符，需要更新")
		for mem in MemberList:
			if  mem['UserName'] not in cr_list[UserName]['MemberList']:
				cr_list[UserName]['MemberList'][mem['UserName']] = {'NickName':mem['NickName'],"count":0}
	else:
		print("成员人数相等，无需更新")


def myupdate_chatroom_mem(cr_list,UserName,MemberList):
	if UserName not in cr_list:
		print("群信息不存在")	
		return False
	for mem in MemberList:
		if  mem['UserName'] not in cr_list[UserName]['MemberList']:
			cr_list[UserName]['MemberList'][mem['UserName']] = {'NickName':mem['NickName'],"count":0}
	return True


@itchat.msg_register([TEXT, PICTURE, FRIENDS, CARD, MAP, SHARING, RECORDING, ATTACHMENT, VIDEO], isGroupChat=True)
def receive_msg(msg):
	global chatroom_list
	if 'ActualNickName' in msg:
		#ToUserName = msg['ToUserName']  # 来自哪个群聊
		ToUserName = msg['FromUserName']  # 来自哪个群聊
		if ToUserName[1] != '@':
			print("来自自己的消息")
			ToUserName = msg['ToUserName']  # 来自哪个群聊
		#FromUserName = msg['FromUserName']  # 谁发的
		FromUserName = msg['ActualUserName']  # 谁发的
		'''
		print "------------"
		print FromUserName
		print ToUserName
		print ToUserName[1]
		print "++++++++++++"
		'''
		if ToUserName in chatroom_list:
			if FromUserName in chatroom_list[ToUserName]['MemberList']:
				chatroom_list[ToUserName]['MemberList'][FromUserName]['count']+=1
				print("来自",chatroom_list[ToUserName]['NickName'],"成员",chatroom_list[ToUserName]['MemberList'][FromUserName]['NickName'],"计数",chatroom_list[ToUserName]['MemberList'][FromUserName]['count'])
			else:
				print("未找到用户信息，更新")
				myupdate_chatroom_mem(chatroom_list,msg['User']['UserName'],msg['User']['MemberList'])
				if FromUserName in chatroom_list[ToUserName]['MemberList']:
					chatroom_list[ToUserName]['MemberList'][FromUserName]['count']+=1
					print("来自",chatroom_list[ToUserName]['NickName'],"成员",chatroom_list[ToUserName]['MemberList'][FromUserName]['NickName'],"计数",chatroom_list[ToUserName]['MemberList'][FromUserName]['count'])
				else:
					print(FromUserName)
					print(ToUserName)
					json_dicts=json.dumps(chatroom_list,indent=4, ensure_ascii=False)
					print(json_dicts)
					json_dicts=json.dumps(msg,indent=4, ensure_ascii=False)
					print(json_dicts)
					print("未找到用户信息，放弃更新计数")
		else:
			print("新群，更新群信息")
			chatrooms = itchat.get_chatrooms(update=True)  # 获取到当前微信账号中的群聊
			for i in range(0, len(chatrooms)):
				myupdate_chatroom(chatroom_list,chatrooms[i]['UserName'],chatrooms[i]['NickName'],chatrooms[i]['MemberCount'],chatrooms[i]['MemberList'])
			if ToUserName in chatroom_list:
				if FromUserName in chatroom_list[ToUserName]['MemberList']:
					chatroom_list[ToUserName]['MemberList'][FromUserName]['count']+=1
					print("来自",chatroom_list[ToUserName]['NickName'],"成员",chatroom_list[ToUserName]['MemberList'][FromUserName]['NickName'],"计数",chatroom_list[ToUserName]['MemberList'][FromUserName]['count'])
				else:
					print("未找到用户信息，更新")
					myupdate_chatroom_mem(chatroom_list,msg['User']['UserName'],msg['User']['MemberList'])
					if FromUserName in chatroom_list[ToUserName]['MemberList']:
						chatroom_list[ToUserName]['MemberList'][FromUserName]['count']+=1
						print("来自",chatroom_list[ToUserName]['NickName'],"成员",chatroom_list[ToUserName]['MemberList'][FromUserName]['NickName'],"计数",chatroom_list[ToUserName]['MemberList'][FromUserName]['count'])
					else:
						print(FromUserName)
						print(ToUserName)
						json_dicts=json.dumps(chatroom_list, indent=4, ensure_ascii=False)
						print(json_dicts)
						json_dicts=json.dumps(msg,indent=4, ensure_ascii=False)
						print(json_dicts)
						print("2 未找到用户信息，放弃更新计数")
			else:
				print(ToUserName)
				json_dicts=json.dumps(msg,indent=4, ensure_ascii=False)
				print(json_dicts)
				print("没有找到群信息，放弃")
	f=open('wechat.json', 'w')
	f.write(json.dumps(chatroom_list,indent=4, ensure_ascii=False))
	f.close
	tmp=[]
	for key in chatroom_list:
		tmp_x={}
		tmp_x['qunmingcheng'] = chatroom_list[key]['NickName']
		tmp_x['qunrenshu'] = chatroom_list[key]['MemberCount']
		print("群总人数为:", tmp_x['qunrenshu'])
		mem_l=[]
		for mem in chatroom_list[key]['MemberList']:
			if chatroom_list[key]['MemberList'][mem]['count'] != 0:
				mem_l.append(chatroom_list[key]['MemberList'][mem]['NickName'])
		tmp_x['huoyuwrenshu'] = len(mem_l)
		if tmp_x['huoyuwrenshu'] != 0:
			print("活跃人数为:", tmp_x['huoyuwrenshu'])
			tmp_x['huoyuedu'] = tmp_x['huoyuwrenshu']/float(tmp_x['qunrenshu'])
			print("群活跃度为:", tmp_x['huoyuedu'])
		else:
			print('群活跃度为0')
		print("活跃人数为", tmp_x['huoyuwrenshu'])
		tmp_x['yonghu'] = mem_l
		tmp.append(tmp_x)
	f=open('data.json', 'w')
	f.write(json.dumps(tmp, indent=4, ensure_ascii=False))
	f.close
	'''
	json_dicts=json.dumps(chatroom_list,indent=4)
	print(json_dicts)
	'''


chatrooms = itchat.get_chatrooms(update=True)  # 获取到当前微信账号中的群聊
itchat.update_chatroom(chatrooms, detailedMember=True)

for i in range(0, len(chatrooms)):
	print(chatrooms[i]['UserName'],chatrooms[i]['NickName'],chatrooms[i]['MemberCount'])
	myupdate_chatroom(chatroom_list,chatrooms[i]['UserName'],chatrooms[i]['NickName'],chatrooms[i]['MemberCount'],chatrooms[i]['MemberList'])

'''
json_dicts=json.dumps(chatroom_list,indent=4)
print(json_dicts)
'''

#reload(sys)
#sys.setdefaultencoding('utf-8')
#if __name__ == '__main__':
#app.run(debug=True,host='0.0.0.0',port=1138,threaded=True)
#	print "go"
itchat.run()

