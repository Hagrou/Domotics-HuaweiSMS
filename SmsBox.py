import datetime

from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from huawei_lte_api.Connection import SetResponseType
from huawei_lte_api.Connection import GetResponseType
from huawei_lte_api.enums.sms import BoxTypeEnum

class SmsBox:
    """Received/Sent Sms Box"""

    def __init__(self, url: str):
        self.huaweiConnection = Connection(url)  # For limited access, I have valid credentials no need for limited access
        self.huaweiClient = Client(self.huaweiConnection)
        # connection = AuthorizedConnection('http://admin:MY_SUPER_TRUPER_PASSWORD@192.168.8.1/', login_on_demand=True) # If you wish to login on demand (when call requires authorization), pass login_on_demand=True
        # connection = AuthorizedConnection('http://admin:admin@192.168.8.1/')

    """
        Wrapper for sms_count
        :return message counter for all boxes
    """
    def counter(self) -> GetResponseType:
        return self.huaweiClient.sms.sms_count()
    """ 
        Remove all Msg in Boxes
        :return: number of deleted msg
    """
    def emptyLocal(self) -> int:
        count = 0
        count += self.emptyBox(BoxTypeEnum.LOCAL_INBOX)
        count += self.emptyBox(BoxTypeEnum.LOCAL_SENT)
        count += self.emptyBox(BoxTypeEnum.LOCAL_DRAFT)
        count += self.emptyBox(BoxTypeEnum.LOCAL_TRASH)
        return count

    """ 
        Delete all message in an Box
        :param boxType: BoxTypeEnum
        :return: number of deleted msg
    """
    def emptyBox(self, boxType: BoxTypeEnum) -> int:
        count = 0
        boxContent = self.huaweiClient.sms.get_sms_list(1, boxType, 20, 0, 0, 1)

        while boxContent['Messages'] is not None:
            msgLeft = list()
            if isinstance(boxContent['Messages']['Message'],dict): # only one message in box
                msgLeft = [boxContent['Messages']['Message']]
            else:
                msgLeft = boxContent['Messages']['Message']
            for msg in msgLeft:
                self.huaweiClient.sms.delete_sms(msg['Index'])
                count += 1
            boxContent = self.huaweiClient.sms.get_sms_list(1, boxType, 20, 0, 0, 1)
        return count

    """ Read all sms """
    def read(self,boxType: BoxTypeEnum, clean: bool=True):
        smsStatus = self.huaweiClient.sms.sms_count()

        print(smsStatus)
        print("***********************************")
        print("* Inbox: %d (%d unread)" % (int(smsStatus['LocalInbox']), int(smsStatus['LocalUnread'])))
        print("* Sent:  %d" % (int(smsStatus['LocalOutbox'])))
        print("* Draft: %d" % (int(smsStatus['LocalDraft'])))
        # print("* #%d sms in box\n " % nbSms)
        print("***********************************")

        smsList = self.huaweiClient.sms.get_sms_list(1, BoxTypeEnum.LOCAL_INBOX, 50, 0, 0, 1)

    """ 
        Send a message to a destlist of receiver
        :param numTel: phone number 
        :param msg: sms message
        :param withTimeStamp: insert time stamp at the beginning of the message
        :return: (OK, sent msg txt)
        
        Example:
        msgBox.sendAll('+33650284422','Hello All'])
    """
    def sendTo(self, numTel: str, msg: str, withTimeStamp = False) -> SetResponseType :
        return self.sendAll([numTel], msg, withTimeStamp)

    """ 
        Send a message to a list of receiver
        :param numTel: list of phone number 
        :param msg: sms message
        :param withTimeStamp: insert time stamp at the beginning of the message
        :return: (OK, sent msg txt)
        
        Example:
        msgBox.sendAll(['+33650284422','+33740342312'],'Hello All'])
    """
    def sendAll(self, strNumList: list, msg: str, withTimeStamp = False) -> (SetResponseType, str):
        if withTimeStamp:
            msg=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S-")+msg
        return (self.huaweiClient.sms.send_sms(strNumList, msg),msg)