#!/usr/bin/env python
#-*- coding:UTF-8 -*-

"""

@author Albert.D
@date   2017-6-20
"""

import itchat
from itchat.content import *
import os
import re
import time
import shutil

class Revocation:
    #储存所有消息的字典
    msg_store = {}

    def __init__(self):
        if not os.path.exists("./Cache/"):
            os.mkdir("./Cache/")

    def GetMsgFrom(self, msg):
        """
        获取消息来源：联系人和群名
        return: 联系人和群组
        """
        msg_from = None
        msg_group = None
        if itchat.search_friends(userName=msg['FromUserName']):
            if itchat.search_friends(userName=msg['FromUserName'])['RemarkName']:
                msg_from = itchat.search_friends(userName=msg['FromUserName'])['RemarkName']  # 消息发送人备注
            elif itchat.search_friends(userName=msg['FromUserName'])['NickName']:  # 消息发送人昵称
                msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']  # 消息发送人昵称
            else:
                msg_from = r"读取好友失败"
        else:
            msg_from = msg.get('ActualNickName', "")
            if not msg_from:
                msg_from = itchat.search_friends(userName=msg['FromUserName'])

        if itchat.search_chatrooms(userName=msg['FromUserName']):
            msg_group = r'[ '
            msg_group += itchat.search_chatrooms(userName=msg['FromUserName'])['NickName']
            msg_group += r' ]'
        return msg_from, msg_group

    def SaveAllMsg(self, msg):
        """
        储存所有收到的消息到字典中
        """
        msg_id = msg['MsgId']  # 消息ID
        msg_time = msg['CreateTime']  # 消息时间
        msg_from, msg_group = self.GetMsgFrom(msg)  # 消息来源
        msg_type = msg['Type']  # 消息类型
        msg_content = None  # 保存消息内容
        msg_url = None  # 保存消息URL

        # 保存消息内容到msg_content，如果是Picture、Recording、Attachment、Video类消息会下载相应内容到Cahe
        if msg['Type'] == 'Text':
            msg_content = msg['Text']
        elif msg['Type'] == 'Picture':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            shutil.move(msg_content, r"./Cache/")
        elif msg['Type'] == 'Card':
            msg_content = msg['RecommendInfo']['NickName'] + r" 的名片"
        elif msg['Type'] == 'Map':
            x, y, location = \
                re.search("<location x=\"(.*?)\" y=\"(.*?)\".*label=\"(.*?)\".*",
                          msg['OriContent']).group(1, 2, 3)
            if location is None:
                msg_content = r"纬度->" + x.__str__() + " 经度->" + y.__str__()
            else:
                msg_content = r"" + location
        elif msg['Type'] == 'Sharing':
            msg_content = msg['Text']
            msg_url = msg['Url']
        elif msg['Type'] == 'Recording':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            shutil.move(msg_content, r"./Cache/")
        elif msg['Type'] == 'Attachment':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            shutil.move(msg_content, r"./Cache/")
        elif msg['Type'] == 'Video':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            shutil.move(msg_content, r"./Cache/")
        elif msg['Type'] == 'Friends':
            msg_content = msg['Text']

        #更新字典内容
        self.msg_store.update(
            {msg_id: {"msg_from": msg_from, "msg_time": msg_time, "msg_type": msg_type,
                      "msg_content": msg_content, "msg_url": msg_url, "msg_group": msg_group}})

    def ClearTimeoutMsg(self):
        """
        清理超过撤回时间的信息，他们不可能被撤回啦
        """
        if self.msg_store.__len__() > 0:
            for msgid in list(self.msg_store):
                if time.time() - self.msg_store.get(msgid, None)["msg_time"] > 300.0:  # 超时两分钟
                    item = self.msg_store.pop(msgid)
                    print("已删除消息：", msgid)  #debug

                    # 可下载类消息，并删除相关文件
                    if item['msg_type'] in ['Picture', 'Recording', 'Video', 'Attachment']:
                        os.remove("./Cache/" + item['msg_content'])

    def IsRevokeMsg(self, msg):
        """
        判断消息类型是不是撤回消息
        return：消息ID
        """
        revoke_msg_id = None

        if msg['Type'] == 'Note':
            if re.search(r"\!\[CDATA\[.*撤回了一条消息\]\]", msg['Content']):
                if re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']):
                    revoke_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
                elif re.search("\;msgid\&gt\;(.*?)\&lt", msg['Content']):
                    revoke_msg_id = re.search("\;msgid\&gt\;(.*?)\&lt", msg['Content']).group(1)

            print("收到撤回消息，Msg_id=", revoke_msg_id) #debug
            return revoke_msg_id

    def SendRevokeMsg(self, msg):
        """
        把撤回的消息发送到文件助手
        """
        msg_id = self.IsRevokeMsg(msg)  #获取撤回消息的ID
        msg_content = self.msg_store.get(msg_id, None)  #获取撤回消息的内容

        mytime = time.localtime()
        msg_time = "%s/%s/%s %s:%s:%s" % (
            mytime.tm_year.__str__(), mytime.tm_mon.__str__(), mytime.tm_mday.__str__(), 
            mytime.tm_hour.__str__(),mytime.tm_min.__str__(), mytime.tm_sec.__str__())

        if (msg_id != None) and (msg_content != None):
            sendMsg = ""
            if msg_content['msg_group']:
                sendMsg += "群聊%s中"%(msg_content['msg_group'])
            sendMsg += "'%s'"%(msg_content['msg_from'])
            sendMsg += "在%s撤回了一条消息：\n"%(msg_time)
            if msg_content['msg_type'] == 'Sharing':
                sendMsg += "%s%s" % (msg_content['msg_url'], "\n\n")
            sendMsg += "%s"%(msg_content['msg_content'])

            itchat.send(sendMsg, toUserName = 'filehelper')
            if msg_content['msg_type'] == 'Picture':
                itchat.send_image("./Cache/" + msg_content['msg_content'], toUserName = 'filehelper')
            elif msg_content['msg_type'] == 'Video':
                itchat.send_video("./Cache/" + msg_content['msg_content'], toUserName = 'filehelper')
            elif (msg_content['msg_type'] == 'Attachment') or \
                (msg_content['msg_type'] == 'Recording'):
                itchat.send_file("./Cache/" + msg_content['msg_content'], toUserName = 'filehelper')

            self.msg_store.pop(msg_id)
            if os.path.exists("./Cache/" + msg_content['msg_content']):
                os.remove("./Cache/" + msg_content['msg_content'])

#对所有的消息进行注册
@itchat.msg_register(INCOME_MSG, isFriendChat = True, isGroupChat = True, isMpChat = True)
def Msg_handle(msg):
    #print(msg)  #debug,打印所有消息
    
    rmsg.SaveAllMsg(msg)
    rmsg.SendRevokeMsg(msg)
    rmsg.ClearTimeoutMsg()

if __name__ == '__main__':
    rmsg = Revocation()
    itchat.auto_login(hotReload = True, enableCmdQR = 2)
    itchat.run(debug = True)
