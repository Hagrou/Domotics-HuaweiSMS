from unittest import TestCase
from SmsBox import *
import json
import time
import hashlib

from random import choice
from string import ascii_lowercase

class TestSmsBox(TestCase):
    def setUp(self):
        with open('config_prod.json', 'r') as file:
            self.config = json.load(file)
        self.smsBox=SmsBox(self.config['huawei_url'])

    """
        wait until msgBox counter constraint is valid or timeout 
        
        Example: 
            self.waitUntil(10, {'LocalUnread':'1','LocalInbox':'1','LocalOutbox':'1','LocalDraft':'0','LocalDeleted':'0'})
    """
    def waitUntil(self, timeout: int, constraint:dict) -> bool:
        elapseTime = 0
        startTime = time.time()
        while True:
            time.sleep(1)
            counter = self.smsBox.counter()
            print(counter)
            predicate = True
            for (k,v) in enumerate(constraint):
                predicate = predicate and (counter[v] == constraint[v])
            elapseTime = time.time() - startTime
            if elapseTime > timeout or predicate:
                break
        return predicate

    def test_emptyLocal(self):
        self.smsBox.emptyLocal()
        self.assertTrue(self.waitUntil(10, {'LocalUnread': '0', 'LocalInbox': '0',
                                            'LocalOutbox': '0', 'LocalDraft': '0',
                                            'LocalDeleted': '0'}))
    def test_send(self):
        self.smsBox.emptyLocal()
        (s, msg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],"test_message")
        self.assertTrue(s == 'OK',self.waitUntil(10, {'LocalUnread':'1','LocalInbox':'1',
                                                    'LocalOutbox':'1','LocalDraft':'0',
                                                    'LocalDeleted':'0'}))

    def test_send_withTimeStamp(self):
        self.smsBox.emptyLocal()
        (result, msg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],"test_message", withTimeStamp = True)
        self.assertTrue(result, self.waitUntil(10, {'LocalUnread':'1','LocalInbox':'1',
                                                     'LocalOutbox':'1','LocalDraft':'0',
                                                     'LocalDeleted':'0'}))

    def test_sendAll(self):
        self.smsBox.emptyLocal()
        (result, msg) = self.smsBox.sendAll([self.config['sim_card_phone_number'],self.config['sim_card_phone_number']], "test_message")
        self.assertTrue(result, self.waitUntil(10, {'LocalUnread':'2','LocalInbox':'2',
                                                       'LocalOutbox':'1','LocalDraft':'0',
                                                       'LocalDeleted':'0'}))



    def test_read_with_no_sms(self):
        self.smsBox.emptyLocal()
        self.waitUntil(10, {'LocalUnread': '0', 'LocalInbox': '0',
                            'LocalOutbox': '0', 'LocalDraft': '0',
                            'LocalDeleted': '0'})

        (result,msg)=self.smsBox.read(BoxTypeEnum.LOCAL_INBOX)

    def test_read_one_msg(self):
        self.smsBox.emptyLocal()
        # 604+504

        (result, msg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],
                                      "[1." + "".join(choice(ascii_lowercase) for i in range(150)) + "]")
        self.assertTrue(result)
        self.waitUntil(10, {'LocalUnread': '1', 'LocalInbox': '1',
                            'LocalOutbox': '1', 'LocalDraft': '0',
                            'LocalDeleted': '0'})
        sha1MsgSent = hashlib.sha1()
        sha1MsgSent.update(bytes(msg,"utf8"))
        sha1MsgSent.digest()

        (result,msgRec)=self.smsBox.read(BoxTypeEnum.LOCAL_INBOX)

        sha1MsgRec = hashlib.sha1()

        sha1MsgRec.update(bytes(msgRec['Content'], "utf8"))
        sha1MsgRec.digest()
        self.assertTrue(sha1MsgSent.digest() == sha1MsgRec.digest())

    def test_read_latest_msg(self):
        self.smsBox.emptyLocal()
        (result, latestMsg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],
                                      "[1." + "".join(choice(ascii_lowercase) for i in range(150)) + "]")
        self.assertTrue(result)
        (result, OtherMsg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],
                                           "[2." + "".join(choice(ascii_lowercase) for i in range(150)) + "]")
        self.assertTrue(result)
        self.waitUntil(10, {'LocalUnread': '2', 'LocalInbox': '2',
                            'LocalOutbox': '2', 'LocalDraft': '0',
                            'LocalDeleted': '0'})
        sha1LatestMsg = hashlib.sha1()
        sha1LatestMsg.update(bytes(latestMsg,"utf8"))
        sha1LatestMsg.digest()

        (result,msgRec)=self.smsBox.read(BoxTypeEnum.LOCAL_INBOX)

        sha1MsgRec = hashlib.sha1()
        sha1MsgRec.update(bytes(msgRec['Content'], "utf8"))
        sha1MsgRec.digest()
        self.assertTrue(sha1LatestMsg.digest() == sha1MsgRec.digest())

    def test_read_big_msg(self):
        self.smsBox.emptyLocal()
        (result, latestMsg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],
                                      "[1." + "".join(choice(ascii_lowercase) for i in range(300)) + "]")
        self.assertTrue(result)
        print(latestMsg)

        self.waitUntil(10, {'LocalUnread': '1', 'LocalInbox': '1',
                            'LocalOutbox': '1', 'LocalDraft': '0',
                            'LocalDeleted': '0'})
        sha1LatestMsg = hashlib.sha1()
        sha1LatestMsg.update(bytes(latestMsg,"utf8"))
        sha1LatestMsg.digest()

        (result,msgRec)=self.smsBox.read(BoxTypeEnum.LOCAL_INBOX)
        print(msgRec['Content'])
        sha1MsgRec = hashlib.sha1()
        sha1MsgRec.update(bytes(msgRec['Content'], "utf8"))
        sha1MsgRec.digest()
        self.assertTrue(sha1LatestMsg.digest() == sha1MsgRec.digest())

    def test_read_all_msg(self):
        self.smsBox.emptyLocal()

        sentMsg=[]
        for i in range(0,9):
            (result, msg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],
                                               "[%d:" % i+"".join(choice(ascii_lowercase) for j in range(150)) + "]")
            sentMsg.insert(i,msg)
            self.assertTrue(result)
            time.sleep(1)

        self.waitUntil(10, {'LocalUnread': '10', 'LocalInbox': '10',
                            'LocalOutbox': '10', 'LocalDraft': '0',
                            'LocalDeleted': '0'})

        i=0
        while True:
            (result,msgRec)=self.smsBox.read(BoxTypeEnum.LOCAL_INBOX)
            if msgRec is None: break
            sha1SentMsg = hashlib.sha1()
            sha1SentMsg.update(bytes(sentMsg[i], "utf8"))
            sha1SentMsg.digest()
            sha1RecMsg = hashlib.sha1()
            sha1RecMsg.update(bytes(msgRec['Content'], "utf8"))
            sha1RecMsg.digest()

            print(msgRec)
            self.assertTrue(sha1SentMsg.digest() == sha1RecMsg.digest())
            i += 1