from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Request,OopsEventsOfReq,QueueReceipt,Receipt
import datetime
from Telegram.TelegramEngine import ExecTelegram
from viber.ViberEngine import ExecViber
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
import os
from django.http import FileResponse
from wsgiref.util import FileWrapper

# Create your views here.
@csrf_exempt
def index(request):
    return HttpResponse(status=404)

def viber(request):
    if(request.body.decode("utf-8")!=''):
        p = Request(Messanger='viber',requesttext = request.body.decode("utf-8"))
        p.save()
        received_json_data = json.loads(request.body.decode("utf-8-sig"))
        if(type(received_json_data)==str):
            received_json_data = json.loads(received_json_data)
        if (received_json_data['event'] == 'message'):
            messagestr = received_json_data['message']
            exec = ExecViber()
            id = str(messagestr['from']['id'])
            exec.SelectAction(id, messagestr)
    return HttpResponse(status=200)

def viberfiles(request):
    _file = 'C:\distrib\Floppy.png'
    filename = os.path.basename(_file)
    response = FileResponse(FileWrapper(open(_file, 'rb')), content_type='application/png')
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

@csrf_exempt
def telegram(request):
    if request.method == 'POST':
        if(request.body.decode("utf-8")!=''):
            p = Request(Messanger='telegram',requesttext = request.body.decode("utf-8"))
            p.save()
            received_json_data = json.loads(request.body.decode("utf-8-sig"))
            if (type(received_json_data) == str):
                received_json_data = json.loads(received_json_data)
                messagestr = received_json_data['message']
            if(received_json_data['message']['from']['is_bot']==False):
                messagetext = messagestr['text']
                id = str(messagestr['from']['id'])
                exec = ExecTelegram()
                exec.SelectAction(id,messagetext)
                try:
                    chatdata =received_json_data['chat']
                    chatid = chatdata['id']
                    exec.SendMessage(chatid,'В целях конфиденциальности данный бот не отвечает в чаты. На все сообщения боту в данном чате будет отвечено в личном сообщении обратившимся пользователям')
                except:
                    notchat = True


        return HttpResponse(status=200)

def RNG(request):
    if request.method == 'POST':
        if(request.body.decode("utf-8")!=''):
            received_json_data = json.loads(request.body.decode("utf-8-sig"))
            if (type(received_json_data) == str):
                received_json_data = json.loads(received_json_data)
                messagestr = received_json_data['Action']
                if(messagestr=='StartAfterNonActive'):
                    QuerySetids = OopsEventsOfReq.objects.get(datetime__gt=datetime.datetime.now() + timedelta(hours=12))
                    for dataid in QuerySetids:
                        id = dataid['chatid']
                        exec = ExecTelegram()
                        exec.SendMessage(id, 'С Вашего аккаунта было обращение к боту ООО "НОВАТЭК-Кострома" во время проведения регламентых работ. Сообщаем Вам, что в настоящее время функционал работает в полном объеме')
                        p = OopsEventsOfReq.objects.get(chatid=id)
                        p.delete()
                elif(messagestr=='GetQueueReceipt'):
                    queue = QueueReceipt.objects.all()
                    list = []
                    for data in queue:
                        list.append({'chatid':data['chatid'],'ls':data['ls'],'month':data['month']})
                    return JsonResponse(list, safe=False)
                elif (messagestr == 'SetFileIDReciept'):
                    data = received_json_data['data']
                    listOK = []
                    listFAIL = []
                    for eldata in data:
                        try:
                            chatid  = eldata['chatid']
                            ls = eldata['ls']
                            month = eldata['month']
                            file_id = eldata['file_id']
                            obj = QueueReceipt.objects.get(chatid=chatid,ls=ls)
                            obj.delete()
                            Receipt.objects.update_or_create(chatid=chatid, ls=ls, month=month,file_id = file_id,
                                                                  defaults={'chatid':chatid, 'ls': ls,
                                                                            'month': month,'file_id': file_id})
                            listOK.append({'chatid':chatid, 'ls': ls})
                        except :
                            listFAIL.append({'chatid': chatid, 'ls': ls})

                    return JsonResponse({'successlist':listOK,'faillist':listFAIL}, safe=False)
                return HttpResponse(status=200)
    return HttpResponse(status=404)

def log(request):
    base_dir = settings.BASE_DIR
    requests = Request.objects.all()
    context  = {
        'requests': requests,
        'base_dir':base_dir
        }
    return render(request, 'log.html',context)


