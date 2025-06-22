import time
class Meeting:
    def __init__(self,meetingId,passkey,host,title):
        self.title=title
        self.meeting_id=meetingId
        self.__passkey=passkey
        self.host=host
        self.members=[]
        self.co_host=[]
        self.messages=[]
    def upadte_members(self,member):
        self.members.append(member)
    def update_co_host(self,member):
        self.co_host=member
    def get_passkey(self):
        return self.__passkey


class User:
    def __init__(self, name, email, password, isLive, isBlocked):
        self.name = name
        self.email = email
        self.__password = password
        self.isLive = isLive
        self.isBlocked = isBlocked
        self.meetings=[]
        

class Messages:
    def __init__(self,data,owner):
        self.owner=owner
        self.data=data
        self.created=time.time()
        
        
