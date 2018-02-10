import json
import requests
from django.http import JsonResponse
from viberapp.models import sessionstate,tokenToSnapping,AccountLinkToId,OopsEventsOfReq,Contacts,Receipt,QueueReceipt
from django.core.exceptions import ObjectDoesNotExist
import time
import os
import datetime
from RNGWebServEngine.RNGWebServices import RNGConnector

sessiontime = 3600
loginRNG = ""
passRNG = ""
TokenViber = '46e547aa43e7d4dd-825e96ff5018ef1d-eef9450dfdce6f70'
hostviber = 'https://chatapi.viber.com'
sender = {'name':'Novatek-Kostroma','avatar':'http://gas-kostroma.ru/images/common/logo-kostroma.jpg'}
ImageSetl = "https://image.ibb.co/hPy8uw/image.png"
ImageMeter = "https://image.ibb.co/j3tNnG/image.png"
ImageContacts = "https://image.ibb.co/gcqwEw/image.png"
ImageReciept= "https://image.ibb.co/ckiyWm/image.png"
ImageHistory= "https://image.ibb.co/jSdJxR/image.png"
ImageSettings= "https://image.ibb.co/ckiyWm/image.png"
ImageHome = "http://image.ibb.co/jwvR6m/home.png"
viberfilehost = 'http://localhost'
diroffiles = '/'

class ExecViber():
    ls = []
    lsact = ''

    def GetAccounts(self, id):
        try:
            QuerySetLschet = AccountLinkToId.objects.get(id=id)
            self.ls = QuerySetLschet
        except ObjectDoesNotExist:
            self.ls = ''
        if (self.ls != ''):
            try:
                QuerySetLschet = AccountLinkToId.objects.get(id=id, current=True)
                if QuerySetLschet.count() == 1:
                    self.lsact = QuerySetLschet[0]['lschet']
                else:
                    AccountLinkToId.objects.filter(id=id).update(current=False)
                    self.lsact = self.ls[0]['lschet']
                    AccountLinkToId.objects.filter(id=id, lschet=self.lsact).update(current=True)
            except ObjectDoesNotExist:
                self.lsact = self.ls[0]['lschet']

    def SelectAction(self, id, messagetext):
        messagetext = self.SOCRLP(messagetext)
        self.GetAccounts(id)
        try:
            sessionstr = sessionstate.objects.get(id=id)
            session = sessionstr['state']
            data1 = sessionstr['data1']
            data2 = sessionstr['data2']
            sessiondatetime = sessionstr['datetime']
            t = datetime.datetime.now()
            delta = t - sessiondatetime
            if (delta.seconds > sessiontime):
                session = ''
                sessiondata1 = ''
                sessiondata2 = ''
            sessionstr.delete()
        except:
            session = ''
            sessiondata1 = ''
            sessiondata2 = ''
        if messagetext == 'Главное меню':
            self.SendMain(id)
        elif messagetext == 'История показаний ПУ':
            if (self.lsact != ''):
                datajson = self.ExecInRNG(id, 'Messendger_GetMeterHistory', {'account': self.lsact})
                data = json.loads(datajson)
                history = data['history']
                if (history.count() > 0):
                    responsetext = '<p>История передачи показаний приборов учета:<br>'
                    for meterData in history:
                        responsetext = responsetext + meterData['MeterSTR'] + '<br>'
                        responsetext = self.CreateTabMeter(responsetext, meterData['Data'])
                    responsetext = responsetext + '</p>'
            else:
                responsetext = '<p>Нет ни одного лицевого счета, привязанного к Вашему аккаунту!!!' + '<br></p>'
            self.SendMessage(id, responsetext)
            self.SendLinkToMain(id)
        elif messagetext == 'Взаиморасчеты':
            if (self.lsact != ''):
                datajson = self.ExecInRNG(id, 'Messendger_settlements',
                                          {'account': self.lsact})
                if (datajson != ''):
                    data = json.loads(datajson)
                    responsetext = '<p>Данные по взаиморасчетам:<br>'
                    responsetext = responsetext + 'Долг на ' + str(data['Month']) + ' - ' + str(data['Saldo']) + '<br>'
                    responsetext = responsetext + 'Начислено за ' + str(data['MonthSTR']) + ' - ' + str(
                        data['Nachisleno']) + '<br>'
                    responsetext = responsetext + 'Оплачено ' + ' - ' + str(data['Oplacheno']) + '<br>'
                    responsetext = responsetext + 'К оплате ' + ' - ' + str(data['KOplate']) + '<br></p>'
                    self.SendMessage(id, responsetext)
            else:
                responsetext = '<p>Нет ни одного лицевого счета, привязанного к Вашему аккаунту!!!' + '<br></p>'
                self.SendMessage(id, responsetext)
        elif messagetext == 'Передать показания счетчика':
            datameterjson = self.ExecInRNG(id, 'Messendger_GetMeters',
                                           {'account': self.lsact})
            if (datameterjson != ''):
                data = json.loads(datameterjson)
                listofmeters = data['meters']
                listofbadmeters = data['metersbad']
                if (listofbadmeters.count() > 0):
                    strbad = ''
                    for badmeter in listofbadmeters:
                        strbad = strbad + '' + badmeter
                    responsetext = 'По следующим приборам учета ввод показаний невозможен из-за наступления срока поверки: ' + strbad
                    self.SendMessage(id, responsetext)
                count = listofmeters.count()
                if (count > 0):
                    if (count > 1):
                        keyboard = self.CreateSimpleKeyboard(6,1, listofmeters)
                        responsetext = 'Выберите прибор учета?'
                        self.SendMessage(id, responsetext,keyboard)
                        sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                              defaults={'id': id, 'state': messagetext})
                    else:
                        datameter = data['datameter']
                        responsetext = 'Введите показания прибора учета ' + listofmeters[0] + '. Предыдущие ' + str(
                            datameter['readout']) + ' от ' + str(datameter['datereadout'].date())
                        self.SendMessage(id, responsetext)
                        textstate = 'setreadout'
                        sessionstate.objects.update_or_create(id=id, state=textstate, data1=datameter['MeterGUID'],
                                                              defaults={'id': id, 'state': textstate,
                                                                        'data1': datameter['MeterGUID']})

                else:
                    responsetext = 'По л/с отсутствуют активные счетчики!!!'
                    self.SendMessage(id, responsetext)
                    self.SendLinkToMain(id)
        elif messagetext == 'Квитанция':
            if (self.lsact != ''):
                datajson = self.ExecInRNG(id, 'Messendger_GetMonth')
                if (datajson != ''):
                    data = json.loads(datajson)
                    Month = data['Month']
                    ReadyReciept = True
                    Queue = False
                    try:
                        QuerySet = Receipt.objects.get(chatid=id, month=Month, ls=self.lsact)
                        t = datetime.datetime.now()
                        datetimeprint = QuerySet[0]['datetime']
                        delta = t - datetimeprint
                        if (delta.seconds < 3600 * 24):
                            file_id = QuerySet[0]['file_id']
                        else:
                            ReadyReciept = False
                    except ObjectDoesNotExist:
                        ReadyReciept = False
                    try:
                        QuerySet = QueueReceipt.objects.get(chatid=id, ls=self.lsact)
                        Queue = True
                    except ObjectDoesNotExist:
                        Queue = False
                    if (Queue == True):
                        self.SendMessage(id,
                                         'Квитанция по лицевому счету ' + self.lsact + ' находится в очереди на формирование. При готовности будет Вам незамедлительно отправлена!')
                    elif (ReadyReciept == True):
                        self.SendDocument(id, file_id, self.lsact, Month, isnew=False)
                    else:
                        QueueReceipt.objects.update_or_create(chatid=id, ls=self.lsact, month=Month, ready=False,
                                                              defaults={'chatid': id, 'ls': self.lsact, 'month': Month,
                                                                        'ready': False})
                        self.SendMessage(id,
                                         'Квитанция по лицевому счету ' + self.lsact + ' добавлена в очередь на формирование и при готовности будет Вам незамедлительно отправлена!')

            else:
                responsetext = '<p>Нет ни одного лицевого счета, привязанного к Вашему аккаунту!!!' + '<br></p>'
                self.SendMessage(id, responsetext)
            self.SendLinkToMain(id)
        elif messagetext == 'Выбрать текущий л/с':
            QuerySetLschet = AccountLinkToId.objects.filter(id=id)
            count = QuerySetLschet.count()
            if (count > 0):
                dataflow=[]
                for lschetstr in QuerySetLschet:
                    dataflow.append(lschetstr['lschet'])
                keyboard = self.CreateSimpleKeyboard(6, 1, dataflow)
                responsetext = 'Выберите лицевой счет'
                self.SendMessage(id, responsetext, keyboard)
                sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                            defaults={'id': id, 'state': messagetext})
            else:
                responsetext = 'К вашему аккаунту не привязан ни один лицевой счет'
                self.SendMessage(id, responsetext)
        elif messagetext == 'Просмотреть список л/с':
            QuerySetLschet = AccountLinkToId.objects.filter(id=id)
            if(QuerySetLschet.count()>0):
                responsetext = ""
                i=1
                for lschetstr in QuerySetLschet:
                    responsetext = str(i)+')'+responsetext+lschetstr['lschet']+'<br>'
                    i=i+1
            else:
                responsetext = 'К вашему аккаунту не привязан ни один лицевой счет'
            self.SendMessage(id, responsetext)
        elif messagetext == 'Привязать л/с к аккаунту':
            responsetext = 'Введите идентификатор, полученный по т.(4942)395-110 для привязки л/с.Код вводится в нижнем регистре'
            result = self.SendMessage(id, responsetext)
            obj = sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                   defaults={'id': id, 'state': messagetext})
        elif messagetext =='settings' or messagetext=='/settings' or messagetext=='Настройки':
            if self.ls.count()==0:
                responsetext =  "Внимание! К вашему аккаунту нет привязанных л/с. Обратитесь по т. (4942)395-110 для получения кода авторизации"
                self.SendMessage(id,responsetext)
            keyboard = Keyboard()
            keyboard.AddButton(3, 2, "Привязать л/с к аккаунту", "small", "center", "bottom", "reply", "Привязать л/с к аккаунту", "#f6f7f9")
            keyboard.AddButton(3, 2, "Просмотреть список л/с", "small", "center", "bottom", "reply",
                               "Просмотреть список л/с", "#f6f7f9")
            keyboard.AddButton(3, 2, "Выбрать текущий л/с", "small", "center", "bottom", "reply", "Выбрать текущий л/с",
                               "#f6f7f9")
            keyboard.AddButton(3, 2, "Главное меню", "small", "center", "bottom", "reply", "Главное меню", "#f6f7f9")
            self.SendMessage(id, 'Выберите действие', keyboard.CreateKeyboard())
        elif messagetext =='help' or messagetext=='/help' or messagetext == 'start' or messagetext == '/start':
            responsetext ="Бот для получения информации по взаиморасчетам, передачи показаний счетчика, получения платежного документа по поставщику газа на территории Костромской области ООО 'НОВАТЭК-Кострома' <br>"
            if self.ls.count()!=0:
                responsetext = 'Текущий выбранный л/с '+self.lsact+'<br>'
                if self.ls.count() > 1:
                    responsetext = responsetext + 'Всего за аккаунтом закреплено ' + self.ls.count()+ ' л/с <br>'
                responsetext = responsetext + 'Для привязки л/с к аккаунту обратитесь по т. (4942)395-110'
            self.SendMessage(id, responsetext)
        elif messagetext == 'Адреса пунктов обслуживания':
            dataflow = ['Кострома', 'Волгореченск', 'Нерехта', 'Красное-на-Волге',
                        'Буй', 'Сусанино','Судиславль', 'Галич']
            responsetext = 'Выберите ближайший населенный пункт?'
            kb = self.CreateSimpleKeyboard( 3, 1, dataflow)
            self.SendMessage(id, responsetext, kb)
            sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                  defaults={'id': id, 'state': messagetext})
        else:
            if (session == ''):
                self.SendMain(id)
            else:
                if (session == 'Привязать л/с к аккаунту'):
                    try:
                        lschetstr = tokenToSnapping.objects.get(tokenid=messagetext, messanger='telegram')
                        lschet = lschetstr['lschet']
                        responsetext = 'К Вашему аккаунту был привязан л/с ' + lschet + '<br>'
                        obj = AccountLinkToId.objects.update_or_create(lschet=lschet, id=id,
                                                                       defaults={'lschet': lschet, 'id': id})
                        p = sessionstate.objects.get(id=id)
                        p.delete()
                        lschetstr.delete()
                    except:
                        responsetext = 'Ошибка привязки л/с к аккаунту'
                    self.SendMessage(id, responsetext)
                    self.Cleansession(id)
                elif (session == 'Выбрать текущий л/с'):
                    try:
                        QuerySetLschet = AccountLinkToId.objects.get(id=id, lschet=messagetext)
                        if QuerySetLschet.count() == 1:
                            AccountLinkToId.objects.filter(id=id).update(current=False)
                            AccountLinkToId.objects.filter(id=id, lschet=messagetext).update(current=True)

                        else:
                            self.SendMessage(id, 'Некорректный л/с')
                            self.SendLinkToMain(id)
                    except:
                        self.SendMessage(id, 'Некорректный л/с!!!!')
                        self.SendLinkToMain(id)
                    self.Cleansession(id)
                elif (session == 'Адреса пунктов обслуживания'):
                    if messagetext=='Кострома':
                        dataflow = ['Центральный пункт', 'Фабричный пункт']
                        responsetext = 'Выберите пункт обслуживания?'
                        kb = self.CreateSimpleKeyboard(6, 1, dataflow)
                        self.SendMessage(id, responsetext, kb)
                    else:
                        try:
                            ContactsData = Contacts.objects.get(abonstation=messagetext)
                            Address = ContactsData['Address']
                            Tel = ContactsData['Address']
                            WorkTime = ContactsData['Address']
                            latGPS = ContactsData['latGPS']
                            longGPS = ContactsData['longGPS']
                            text = '<p> Адрес: ' + Address + '<br>' + 'Тел. :' + Tel+'<br>' + 'Рабочее время :' + WorkTime+'</p>'
                            self.SendMessage(id, text)
                            self.SendLocation(id, {"lat": latGPS,"lon":longGPS})
                        except ObjectDoesNotExist:
                            self.SendMessage(id, 'Не найден пункт обслуживания по указанным данным!!!')
                    self.SendLinkToMain(id)
                    self.Cleansession(id)
                elif (session == 'setreadout'):
                    if (sessiondata1 != ''):
                        datameterjson = self.ExecInRNG(id,'Messendger_SetMeterReadOut',{'meterguid': sessiondata1,'readout':messagetext})
                        if (datameterjson != ''):
                            datameter = json.loads(datameterjson)
                            if(datameter['result']==False):
                                self.SendMessage(id, datameter['responsetext'])
                            else:
                                self.SendMessage(id, 'Переданные показания приняты к рассчету!!!')
                            self.Cleansession(id)
                        else:
                            self.SendMain(id)
                    else:
                        self.SendMain(id)
                    self.Cleansession(id)

    def CreateSimpleKeyboard(self,countofcol,countofrow, listof):
        keyboard = Keyboard()
        for object in listof:
            keyboard.AddButton(countofcol, countofrow, object, "small", "center", "bottom", "reply", object)
        return keyboard.CreateKeyboard()

    def SendLinkToMain(self,id):
        keyboard = Keyboard()
        keyboard.AddButton(2, 2, "Главное меню", "small", "center", "bottom", "reply", "Главное меню", "#f6f7f9",
                           ImageHome)
        keyboard.AddButton(2, 2, "Настройки", "small", "center", "bottom", "reply", "Настройки", "#f6f7f9",
                           ImageContacts)
        self.SendMessage(id, 'Выберите действие', keyboard.CreateKeyboard())

    def CreateTabMeter(self, text, readout):
        text = text + '<table border="1">'
        text = text + '<tr><th>Дата показания</th><th>Показание</th><th>Источник</th></tr>'
        for read in readout:
            text = text + '<tr><td>' + read['datereadstr'] + '</td><td>' + read['read'] + '</td><td>' + read[
                'readsource'] + '</td></tr>'
        return text

    def SendDocument(self,id,file_id,ls,month,isnew = True):
        message = {'receiver':id,'min_api_version':1,'sender':sender,'tracking_data':'tracking data','type':'file','media':viberfilehost+'/viberfiles/'+file_id+'.pdf',
                   'size':os.path.getsize(diroffiles + file_id+'.pdf'),'file_name':file_id+'.pdf'}
        headers = {'content-type': 'application/json'}
        res = requests.post(hostviber + '/pa/send_message', json=message, headers=headers)
        if res.status_code == 200:
            return True
        else:
            return False

    def SendMain(self,id):
        keyboard = Keyboard()
        keyboard.AddButton(2,2,"Взаиморасчеты","small","center","bottom","reply","Взаиморасчеты","#f6f7f9",
                           ImageSetl)
        keyboard.AddButton(2, 2, "Передать показания счетчика", "small", "center", "bottom", "reply", "Передать показания счетчика", "#f6f7f9",
                           ImageMeter)
        keyboard.AddButton(2, 2, "Адреса пунктов", "small", "center", "bottom", "reply", "Адреса пунктов", "#f6f7f9",
                           ImageContacts)
        keyboard.AddButton(2, 2, "Квитанция", "small", "center", "bottom", "reply", "Квитанция", "#f6f7f9",
                           ImageContacts)
        keyboard.AddButton(2, 2, "История показаний ПУ", "small", "center", "bottom", "reply", "История показаний ПУ", "#f6f7f9",
                           ImageContacts)
        keyboard.AddButton(2, 2, "Настройки", "small", "center", "bottom", "reply", "Настройки", "#f6f7f9",
                           ImageContacts)
        self.SendMessage(id,'Выберите действие',keyboard.CreateKeyboard())

    def SOCRLP(self, text):
        return ' '.join(text.split())

    def ExecInRNG(self,id,algname,params):
        datameterjson = ''
        try:
            RNG = RNGConnector()
            res = RNG.Connect()
            if(res!=False):
                datameterjson = RNG.Execute(algname, JsonResponse(params, safe=False))
            else:
                self.SendMessage(id,
                                 'В данный момент проводятся регламентные работы. Повторите попытку позже. Приносим извинения за доставленные неудобства.')
                OopsEventsOfReq.objects.update_or_create(id=id,defaults={'id': id})
                self.SendLinkToMain(id)
        except:
            self.SendMessage(id,
                             'В данный момент проводятся регламентные работы. Повторите попытку позже. Приносим извинения за доставленные неудобства.')
            self.SendLinkToMain(id)
        return datameterjson

    def Cleansession(self, id):
        sessionstr = sessionstate.objects.get(id=id)
        sessionstr.delete()

    def SendMessage(self,id, text,keyboard=''):
        message = structSendMessage(id, text,'',keyboard)
        headers = {'content-type': 'application/json'}
        res = requests.post(hostviber + '/pa/send_message', json=message, headers=headers)
        if res.status_code == 200:
            return True
        else:
            return False

    def SendMessageLocation(self, id, location=''):
        message = structSendMessage(id, '', 'location','',location)
        headers = {'content-type': 'application/json'}
        res = requests.post(hostviber + '/pa/send_message', json=message, headers=headers)
        if res.status_code == 200:
            return True
        else:
            return False

def structSendMessage(chat_id = '', text = ' ', type='text',keyboard='',location=''):
    if keyboard=='':
        return {'receiver':chat_id,'min_api_version':1,'sender':sender,'tracking_data':'tracking data','type':type,'text':text}
    elif type=='location':
        return {'receiver': chat_id, 'min_api_version': 1, 'sender': sender, 'tracking_data': 'tracking data',
                'type': type, 'location': location}
    else:
        return {'receiver': chat_id, 'min_api_version': 1, 'sender': sender, 'tracking_data': 'tracking data',
                'type': type, 'text': text, 'keyboard':keyboard}

class Keyboard():
    DefaultHeight = True
    BgColor = "#FFFFFF"
    buttons = []
    def __init__(self,DefaultHeight=True,BgColor="#FFFFFF"):
        self.BgColor = BgColor
        self.DefaultHeight = DefaultHeight

    def AddButton(self,Columns,Rows,Text,TextSize,TextHAlign,TextVAlign,ActionType,ActionBody,BgColor='',Image=""):
        body = {
            "Columns": Columns,
            "Rows": Rows,
            "Text": Text,
            "TextSize": TextSize,
            "TextHAlign": TextHAlign,
            "TextVAlign": TextVAlign,
            "ActionType": ActionType,
            "ActionBody": ActionBody,
            "BgColor": BgColor,
            "Image": Image
        }
        self.buttons.append(body)

    def CreateKeyboard(self):
        return {"Type": "keyboard",
            "BgColor": self.BgColor,
            "DefaultHeight": self.DefaultHeight,
            "Buttons": self.buttons
        }


