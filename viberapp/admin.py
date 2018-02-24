from django.contrib import admin
from viberapp.models import *
admin.site.register([Request, sessionstate,OopsEventsOfReq,Contacts,tokenToSnapping,AccountLinkToId,
                     Receipt,QueueReceipt])
# Register your models here.
