from django.db import models
import datetime

class Request(models.Model):
    requesttext = models.TextField()
    DateTimeField = models.DateTimeField('date created', auto_now_add=True)
    Messanger = models.CharField(max_length=20,default='viber')

class sessionstate(models.Model):
    id = models.CharField(max_length=24,primary_key=True)
    state = models.CharField(max_length=24)
    data1 = models.CharField(max_length=24)
    data2 = models.CharField(max_length=24)
    datetime = models.DateTimeField('date created', auto_now_add=True)
    def __str__(self):
        return self.id+'-'+self.state

class tokenToSnapping(models.Model):
    lschet = models.IntegerField(primary_key=True)
    tokenid = models.IntegerField()
    name = models.CharField(max_length=24)
    messanger = models.CharField(max_length=24,primary_key=True,default='telegram')
    datetime = models.DateTimeField('date created', auto_now_add=True)
    def __str__(self):
        return self.name+'-'+self.lschet

class AccountLinkToId(models.Model):
    lschet = models.CharField(max_length=24,primary_key=True)
    id = models.IntegerField()
    current = models.BooleanField()
    def __str__(self):
        return self.lschet

# class messages(models.Model):
#     text = models.TextField()
#     dtime = models.DateTimeField()
#     message_token = models.CharField(max_length=19)
#     idviber = models.CharField(max_length=24)
#     name = models.CharField(max_length=24)
#     Messanger = models.CharField(max_length=20, default='viber')
#     def __str__(self):
#         return self.name+'-'+str(self.dtime)

# class messagestatus(models.Model):
#     message_token = models.CharField(max_length=19)
#     user_id = models.CharField(max_length=24)
#     status = models.CharField(max_length=12)
#     dtime = models.DateTimeField(default=datetime.datetime.now())
#     def __str__(self):
#         return self.user_id+'-'+str(self.dtime)

# class viberid(models.Model):
#     idviber = models.CharField(max_length=24, primary_key=True)
#     subscribed = models.BooleanField()
#     name = models.CharField(max_length=24,default='oleg')
#     datetime = models.DateTimeField('date created', auto_now_add=True)
#     def __str__(self):
#         return self.name+'-'+self.idviber

# class telegrammchatid(models.Model):
#     chatid = models.CharField(max_length=24, primary_key=True)
#     name = models.CharField(max_length=24,default='oleg')
#     datetime = models.DateTimeField('date created', auto_now_add=True)
#     def __str__(self):
#         return self.name+'-'+self.chatid

class QueueReceipt(models.Model):
    chatid = models.CharField(max_length=24, primary_key=True)
    ls = models.CharField(max_length=10)
    datetime = models.DateTimeField('date created', auto_now_add=True)
    month = models.DateField()
    ready = models.BooleanField()
    def __str__(self):
        return self.ls + '-' + self.chatid

class Receipt(models.Model):
    chatid = models.CharField(max_length=24, primary_key=True)
    ls = models.CharField(max_length=10)
    file_id = models.DateTimeField(max_length=10)
    datetime = models.DateTimeField('date created', auto_now_add=True)
    month = models.DateField()
    def __str__(self):
        return self.ls + '-' + self.chatid

class OopsEventsOfReq(models.Model):
    chatid = models.CharField(max_length=24, primary_key=True)
    datetime = models.DateTimeField('date created', auto_now_add=True)
    def __str__(self):
        return self.chatid+'-'+self.datetime

class Contacts(models.Model):
    abonstation= models.CharField(max_length=24, primary_key=True)
    Address = models.CharField(max_length=300)
    Tel = models.CharField(max_length=100)
    WorkTime = models.CharField(max_length=100)
    latGPS = models.FloatField(default=0)
    longGPS = models.FloatField(default=0)
    def __str__(self):
        return self.abonstation

