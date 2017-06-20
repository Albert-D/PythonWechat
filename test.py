#!/usr/bin/env python
#-*- coding:UTF-8 -*-

"""
"""

import itchat
from itchat.content import *
import os
import re


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
