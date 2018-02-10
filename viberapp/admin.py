from django.contrib import admin
from viberapp.models import *
admin.site.register([Request,accounts,messages,messagestatus,viberid,telegrammchatid,
                     sessionstate,OopsEventsOfReq,Contacts,tokenToSnapping,AccountLinkToIdTelegram,
                     Receipt,QueueReceipt])
# Register your models here.
