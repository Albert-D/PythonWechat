#!/usr/bin/env python
#-*- coding:UTF-8 -*-

"""
"""

import itchat
from itchat.content import *
import os
import re

class Revocation():
    #储存所有消息的字典
    msg_store = {}

    def __init__(self):
        if not os.path.exists(".\\Cache\\"):
            os.mkdir(".\\Cache\\")
        if not os.path.exists(".\\Revocation\\"):
            os.mkdir(".\\Revocation\\")

    def SaveAllMsg(self, msg):
        """
        储存所有收到的消息到字典中
        """
        msg_id = msg['MsgId']  # 消息ID
        msg_time = msg['CreateTime']  # 消息时间
        msg_from, msg_group = self.GetMsgFrom(msg)  # 消息来源
        msg_type = msg['Type']  # 消息类型
        msg_content = None  # 根据消息类型不同，消息内容不同
        msg_url = None  # 分享类消息有url

        msg_id = msg['MsgId']  # 消息ID
        msg_time = msg['CreateTime']  # 消息时间
        msg_from, msg_group = self.GetMsgFrom(msg)  # 消息来源
        msg_type = msg['Type']  # 消息类型
        msg_content = None  # 根据消息类型不同，消息内容不同
        msg_url = None  # 分享类消息有url

        # 图片 语音 附件 视频，可下载消息将内容下载暂存到当前目录
        if msg['Type'] == 'Text':
            msg_content = msg['Text']
        elif msg['Type'] == 'Picture':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            shutil.move(msg_content, r".\\Cache\\")
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
            shutil.move(msg_content, r".\\Cache\\")
        elif msg['Type'] == 'Attachment':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            shutil.move(msg_content, r".\\Cache\\")
        elif msg['Type'] == 'Video':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])
            shutil.move(msg_content, r".\\Cache\\")
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

                    # 可下载类消息，并删除相关文件
                    if item['msg_type'] in ['Picture', 'Recording', 'Video', 'Attachment']:
                        os.remove(".\\Cache\\" + item['msg_content'])

    def IsRevokeMsg(self, msg):
        """
        判断消息类型是不是撤回消息
        return：消息ID
        """
        revoke_msg_id = None

        itchat.search_chatrooms()
        if re.search(r"\!\[CDATA\[.*撤回了一条消息\]\]", msg['Content']):
            if re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']):
                revoke_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
            elif re.search("\;msgid\&gt\;(.*?)\&lt", msg['Content']):
                revoke_msg_id = re.search("\;msgid\&gt\;(.*?)\&lt", msg['Content']).group(1)

        print("收到撤回消息的ID"，revoke_msg_id) #debug
        return revoke_msg_id

#对所有的消息进行注册
@itchat.msg_register(INCOME_MSG, isFriendChat = True, isGroupChat = True, isMpChat = True)
def Msg_handle(msg):
    print(msg)  #debug,打印所有消息
    
    if msg['Type'] == 'Video':
        msg.download(msg.fileName)
        #msg['Text'](msg['FileName'])

if __name__ == '__main__':
    itchat.auto_login(hotReload = True, enableCmdQR = True)
    itchat.run(debug = True)
