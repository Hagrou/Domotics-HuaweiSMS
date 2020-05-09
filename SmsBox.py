import datetime
import getopt
import sys
import time
from huawei_lte_api.Client import Client
from huawei_lte_api.Connection import Connection
from huawei_lte_api.Connection import SetResponseType
from huawei_lte_api.Connection import GetResponseType
from huawei_lte_api.enums.sms import BoxTypeEnum
from huawei_lte_api.exceptions import ResponseErrorException

"""
160 char de 7 bits ou 70 char Unicode 16
Long Sms: ensemble de sms a assembler

Message status report: ack de reception activé dans un flag du sms
Message submission report: ack du serveur de la bonne soumission du sms
Message delivery report: ack de reception du sms


"""
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

    """ Read older message """
    def read(self,boxType: BoxTypeEnum, removeMessage: bool=True) -> (bool,list):
        try:
            boxContent = self.huaweiClient.sms.get_sms_list(1, boxType, 1, 0, 1, 1)
            print(boxContent)

            if boxContent['Messages'] is None: # no message
                return (True, None)
            time.sleep(4) # it can be a big message :/
            boxContent = self.huaweiClient.sms.get_sms_list(1, boxType, 1, 0, 1, 1)
            print(boxContent)
            if isinstance(boxContent['Messages']['Message'],dict): # only one message in box
                msg = boxContent['Messages']['Message']
            else:
                msg = boxContent['Messages']['Message'][0]

            if removeMessage:
                self.huaweiClient.sms.delete_sms(msg['Index'])
            return (True, msg)

        except ResponseErrorException as e:
            return (False, None)

    """ 
        Send a message to a destlist of receiver
        :param numTel: phone number 
        :param msg: sms message
        :param withTimeStamp: insert time stamp at the beginning of the message
        :param maxRetry: maxRetry count if an error occurs
        :return: (OK, sent msg txt)
        
        Example:
        msgBox.sendAll('+33650284422','Hello All'])
    """
    def sendTo(self, numTel: str, msg: str, withTimeStamp = False, maxRetry=10) -> SetResponseType :
        return self.sendAll([numTel], msg, withTimeStamp,maxRetry)

    """ 
        Send a message to a list of receiver
        :param numTel: list of phone number 
        :param msg: sms message
        :param withTimeStamp: insert time stamp at the beginning of the message
        :param maxRetry: maxRetry count if an error occurs
        :return: (OK, sent msg txt)
        
        Example:
        msgBox.sendAll(['+33650284422','+33740342312'],'Hello All'])
    """
    def sendAll(self, strNumList: list, msg: str, withTimeStamp = False, maxRetry=10) -> (SetResponseType, str):
        nbError=0
        result=''

        if withTimeStamp:
            msg=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S-")+msg

        while nbError<maxRetry:
            try:
                result=self.huaweiClient.sms.send_sms(strNumList, msg)
                if result: break
            except ResponseErrorException as e:
                nbError +=1

        return (result, msg)

def usage(value):
    print("SmsBox send or receive Sms")
    print("\t send <phone> <message>")
    print("\t rec")
    exit(value)

def sendSms(phone, msg):
    smsBox=SmsBox("http://192.168.8.1/")
    smsBox.sendTo(phone, msg, withTimeStamp = True)

def main(argv):
    action=None
    phone=None
    msg=None

    print(argv)

    if argv[0] == "send":
        if len(argv) !=3 : usage(1)
        sendSms(argv[1],argv[2])
    else:
        usage()

if __name__ == "__main__":
    main(sys.argv[1:])