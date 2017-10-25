import pymysql

class ConInfo(object):
    def __init__(self):
        self.connection = pymysql.connect(host='mysql', port=3306, user='root', passwd='root', db='tts')
