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


class SmsBox:
    """Received/Sent Sms Box"""

    def __init__(self, url: str):
        self.huaweiConnection = Connection(
            url)  # For limited access, I have valid credentials no need for limited access
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
        :param box_type: BoxTypeEnum
        :return: number of deleted msg
    """

    def emptyBox(self, box_type: BoxTypeEnum) -> int:
        count = 0
        box_content = self.huaweiClient.sms.get_sms_list(1, box_type, 20, 0, 0, 1)

        while box_content['Messages'] is not None:
            msg_left = list()
            if isinstance(box_content['Messages']['Message'], dict):  # only one message in box
                msg_left = [box_content['Messages']['Message']]
            else:
                msg_left = box_content['Messages']['Message']
            for msg in msg_left:
                self.huaweiClient.sms.delete_sms(msg['Index'])
                count += 1
            box_content = self.huaweiClient.sms.get_sms_list(1, box_type, 20, 0, 0, 1)
        return count

    """ Read message """

    def read(self, box_type: BoxTypeEnum, remove_message: bool = True) -> (bool, list):
        try:
            box_content = self.huaweiClient.sms.get_sms_list(1, box_type, 1, 0, 1, 1)

            if box_content['Messages'] is None:  # no message
                return True, None
            time.sleep(4)  # it can be a big message :/
            box_content = self.huaweiClient.sms.get_sms_list(1, box_type, 1, 0, 1, 1)
            if isinstance(box_content['Messages']['Message'], dict):  # only one message in box
                msg = box_content['Messages']['Message']
            else:
                msg = box_content['Messages']['Message'][0]

            if remove_message:
                self.huaweiClient.sms.delete_sms(msg['Index'])
            return True, msg

        except ResponseErrorException as e:
            return (False, None)

    """ 
        Send a message to a destlist of receiver
        :param numTel: phone number 
        :param msg: sms message
        :param withTimeStamp: insert time stamp at the beginning of the message
        :param maxRetry: maxRetry count if an error occurs
        :param clearSentBox: delete sent message
        :return: (OK, sent msg txt)
        
        Example:
        msgBox.sendAll('+33650284422','Hello All'])
    """

    def sendTo(self, numTel: str, msg: str, with_time_stamp: bool = False, max_retry: int = 10,
               clear_sent_box: bool = True) -> SetResponseType:
        return self.sendAll([numTel], msg, with_time_stamp, max_retry, clear_sent_box)

    """ 
        Send a message to a list of receiver
        :param numTel: list of phone number 
        :param msg: sms message
        :param with_time_stamp: insert time stamp at the beginning of the message
        :param max_retry: maxRetry count if an error occurs
        :param clear_sent_box: delete sent message
        :return: (OK, sent msg txt)
        
        Example:
        msgBox.sendAll(['+33650284422','+33740342312'],'Hello All'])
    """

    def sendAll(self, num_list: list, msg: str, with_time_stamp: bool = False, max_retry: int = 10,
                clear_sent_box: bool = True) -> (SetResponseType, str):
        nbError = 0
        result = ''

        if with_time_stamp:
            msg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S-") + msg

        while nbError < max_retry:
            try:
                result = self.huaweiClient.sms.send_sms(num_list, msg)
                if result: break
            except ResponseErrorException as e:
                nbError += 1

        if clear_sent_box:
            self.emptyBox(BoxTypeEnum.LOCAL_SENT)
            self.emptyBox(BoxTypeEnum.LOCAL_DRAFT)
            self.emptyBox(BoxTypeEnum.LOCAL_TRASH)
        return result, msg


def usage(value: int) -> None:
    print("SmsBox send or receive Sms")
    print("\t send <phone> <message>")
    print("\t rec")
    exit(value)


def sendSms(phone: str, msg: str) -> None:
    smsBox = SmsBox("http://192.168.8.1/")
    smsBox.sendTo(phone, msg, with_time_stamp=True)


def main(argv):
    action = None
    phone = None
    msg = None

    print(argv)

    if argv[0] == "send":
        if len(argv) != 3: usage(1)
        sendSms(argv[1], argv[2])
    else:
        usage()


if __name__ == "__main__":
    main(sys.argv[1:])
