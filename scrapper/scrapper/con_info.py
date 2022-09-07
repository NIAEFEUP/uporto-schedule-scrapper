import pymysql

class ConInfo(object):
    def __init__(self):
        self.connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='tts')
