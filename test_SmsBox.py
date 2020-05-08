from unittest import TestCase
from SmsBox import *
import json
import time

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
        (s, msg) = self.smsBox.sendTo(self.config['sim_card_phone_number'],"test_message", withTimeStamp = True)
        self.assertTrue(s == 'OK', self.waitUntil(10, {'LocalUnread':'1','LocalInbox':'1',
                                                     'LocalOutbox':'1','LocalDraft':'0',
                                                     'LocalDeleted':'0'}))

    def test_sendAll(self):
        self.smsBox.emptyLocal()
        (s, msg) = self.smsBox.sendAll([self.config['sim_card_phone_number'],self.config['sim_card_phone_number']], "test_message")
        self.assertTrue(s == 'OK', self.waitUntil(10, {'LocalUnread':'2','LocalInbox':'2',
                                                       'LocalOutbox':'1','LocalDraft':'0',
                                                       'LocalDeleted':'0'}))
