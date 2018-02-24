import json
import requests
from django.http import JsonResponse
from viberapp.models import sessionstate,tokenToSnapping,AccountLinkToId,OopsEventsOfReq,Contacts,Receipt,QueueReceipt
from django.core.exceptions import ObjectDoesNotExist
import time
import datetime
from RNGWebServEngine.RNGWebServices import RNGConnector
from RNGWebServEngine.Trains import TrainConnector

UseTrains = True
hosttrain = ""
logintrains =""
passwordtrains=""
sessiontime = 3600
loginRNG = ""
passRNG = ""
tokenTelegram = ""
hosttelegram ="https://api.telegram.org/bot"

class ExecTelegram():
    ls=[]
    lsact=''
    def GetAccounts(self,id):
        try:
            QuerySetLschet = AccountLinkToId.objects.get(id=id)
            self.ls =QuerySetLschet
        except ObjectDoesNotExist:
            self.ls = ''
        if(self.ls!=''):
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

    def SelectAction(self,id,messagetext):
        messagetext = self.SOCRLP(messagetext)
        self.GetAccounts(id)
        try:
            sessionstr = sessionstate.objects.get(id=id)
            session = sessionstr['state']
            data1 = sessionstr['data1']
            data2 = sessionstr['data2']
            sessiondatetime=sessionstr['datetime']
            t = datetime.datetime.now()
            delta = t-sessiondatetime
            if(delta.seconds>sessiontime):
                session= ''
                sessiondata1 = ''
                sessiondata2 = ''
            sessionstr.delete()
        except:
            session = ''
            sessiondata1 = ''
            sessiondata2 = ''
        if messagetext=='help' or messagetext=='/help' or messagetext == 'start' or messagetext == '/start':
            responsetext ="Бот для получения информации по взаиморасчетам, передачи показаний счетчика, получения платежного документа по поставщику газа на территории Костромской области ООО 'НОВАТЭК-Кострома' <br>"
            if self.ls.count()!=0:
                responsetext = 'Текущий выбранный л/с '+self.lsact+'<br>'
                if self.ls.count() > 1:
                    responsetext = responsetext + 'Всего за аккаунтом закреплено ' + self.ls.count()+ ' л/с <br>'
                responsetext = responsetext + 'Для привязки л/с к аккаунту обратитесь по т. (4942)395-110'
            self.SendMessage(id, responsetext)
        elif messagetext=='settings' or messagetext=='/settings' or messagetext=='Настройки':
            if self.ls.count()==0:
                responsetext =  "Внимание! К вашему аккаунту нет привязанных л/с. Обратитесь по т. (4942)395-110 для получения кода авторизации"
                self.SendMessage(id,responsetext)
            dataflow = ['Привязать л/с к аккаунту','Просмотреть список л/с','Выбрать текущий л/с','Главное меню']
            Keyboard = ReplyKeyboardMarkup()
            Keyboard.create(2,2,dataflow)
            responsetext = 'Выберите действие?'
            Keyboard.SendKeyboard(id, responsetext)
        elif messagetext == 'Привязать л/с к аккаунту':
            responsetext = 'Введите идентификатор, полученный по т.(4942)395-110 для привязки л/с.Код вводится в нижнем регистре'
            result = self.SendMessage(id, responsetext,True)
            obj = sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                   defaults={'id': id, 'state': messagetext})
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
        elif messagetext == 'Выбрать текущий л/с':
            QuerySetLschet = AccountLinkToId.objects.filter(id=id)
            count = QuerySetLschet.count()
            if (count > 0):
                dataflow=[]
                for lschetstr in QuerySetLschet:
                    dataflow.append(lschetstr['lschet'])
                Keyboard = ReplyKeyboardMarkup()
                Keyboard.create(count, 1, dataflow)
                responsetext = 'Выберите лицевой счет?<br>'
                Keyboard.SendKeyboard(id, responsetext)
                sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                            defaults={'id': id, 'state': messagetext})
            else:
                responsetext = 'К вашему аккаунту не привязан ни один лицевой счет'
                self.SendMessage(id, responsetext)
        elif messagetext == 'Главное меню':
            self.SendMain(id)
        elif messagetext == 'Адреса пунктов обслуживания':
            dataflow = ['Кострома', 'Волгореченск', 'Нерехта', 'Красное-на-Волге',
                        'Буй', 'Сусанино','Судиславль', 'Галич']
            Keyboard = ReplyKeyboardMarkup()
            Keyboard.create(2, 4, dataflow)
            responsetext = 'Выберите ближайший населенный пункт?'
            Keyboard.SendKeyboard(id, responsetext)
            sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                  defaults={'id': id, 'state': messagetext})
        elif messagetext == 'История показаний ПУ':
            if (self.lsact != ''):
                datajson = self.ExecInRNG(id, 'Messendger_GetMeterHistory', {'account': self.lsact})
                data = json.loads(datajson)
                history = data['history']
                if(history.count()>0):
                    responsetext = '<p>История передачи показаний приборов учета:<br>'
                    for meterData in history:
                        responsetext = responsetext + meterData['MeterSTR']+'<br>'
                        responsetext =  self.CreateTabMeter(responsetext,meterData['Data'])
                    responsetext=responsetext+'</p>'
            else:
                responsetext = '<p>Нет ни одного лицевого счета, привязанного к Вашему аккаунту!!!' + '<br></p>'
            self.SendMessage(id, responsetext)
            self.SendLinkToMain(id)
        elif messagetext == 'Взаиморасчеты':
            if(self.lsact!=''):
                datajson = self.ExecInRNG(id, 'Messendger_settlements',
                                               {'account': self.lsact})
                if(datajson!=''):
                    data = json.loads(datajson)
                    responsetext = '<p>Данные по взаиморасчетам:<br>'
                    responsetext = responsetext+'Долг на '+str(data['Month'])+ ' - '+str(data['Saldo'])+'<br>'
                    responsetext = responsetext + 'Начислено за ' + str(data['MonthSTR']) + ' - '+str(data['Nachisleno'])+'<br>'
                    responsetext = responsetext + 'Оплачено ' + ' - ' + str(data['Oplacheno']) + '<br>'
                    responsetext = responsetext + 'К оплате ' + ' - ' + str(data['KOplate']) + '<br></p>'
                    self.SendMessage(id, responsetext, True)
            else:
                responsetext = '<p>Нет ни одного лицевого счета, привязанного к Вашему аккаунту!!!'+'<br></p>'
                self.SendMessage(id, responsetext, True)
            self.SendLinkToMain(id)
        elif messagetext == 'Передать показания счетчика':
            Keyboard = ReplyKeyboardMarkup()
            Keyboard.RemoveKeyboard(id)
            datameterjson = self.ExecInRNG(id,'Messendger_GetMeters',
                                           {'account': self.lsact})
            if(datameterjson!=''):
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
                if(count>0):
                    if(count>1):
                        Keyboard = ReplyKeyboardMarkup()
                        Keyboard.create(count, 1, listofmeters)
                        responsetext = 'Выберите прибор учета?'
                        Keyboard.SendKeyboard(id, responsetext)
                        sessionstate.objects.update_or_create(id=id, state=messagetext,
                                                              defaults={'id': id, 'state': messagetext})
                    else:
                        datameter = data['datameter']
                        responsetext = 'Введите показания прибора учета '+listofmeters[0]+'. Предыдущие ' + str(
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
                if(datajson!=''):
                    data = json.loads(datajson)
                    Month = data['Month']
                    ReadyReciept = True
                    Queue = False
                    try:
                        QuerySet = Receipt.objects.get(chatid=id, month=Month,ls=self.lsact)
                        t = datetime.datetime.now()
                        datetimeprint = QuerySet[0]['datetime']
                        delta = t - datetimeprint
                        if (delta.seconds < 3600*24):
                            file_id = QuerySet[0]['file_id']
                        else:
                            ReadyReciept = False
                    except ObjectDoesNotExist:
                        ReadyReciept = False
                    try:
                        QuerySet = QueueReceipt.objects.get(chatid=id,ls=self.lsact)
                        Queue = True
                    except ObjectDoesNotExist:
                        Queue = False
                    if (Queue==True):
                        self.SendMessage(id, 'Квитанция по лицевому счету '+self.lsact+ ' находится в очереди на формирование. При готовности будет Вам незамедлительно отправлена!')
                    elif (ReadyReciept==True):
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
        else:
            if(session==''):
                self.SendMain(id)
            else:
                if(session=='Привязать л/с к аккаунту'):
                    try:
                        lschetstr = tokenToSnapping.objects.get(tokenid=messagetext,messanger='telegram')
                        lschet = lschetstr['lschet']
                        responsetext = 'К Вашему аккаунту был привязан л/с ' + lschet+'<br>'
                        obj = AccountLinkToId.objects.update_or_create(lschet=lschet,id=id,defaults={'lschet': lschet, 'id': id})
                        p = sessionstate.objects.get(id=id)
                        p.delete()
                        lschetstr.delete()
                    except:
                        responsetext = 'Ошибка привязки л/с к аккаунту'
                    self.SendMessage(id, responsetext)
                    self.Cleansession(id)
                elif(session=='Выбрать текущий л/с'):
                    try:
                        QuerySetLschet = AccountLinkToId.objects.get(id=id,lschet=messagetext)
                        if QuerySetLschet.count()==1:
                            AccountLinkToId.objects.filter(id=id).update(current=False)
                            AccountLinkToId.objects.filter(id=id,lschet=messagetext).update(current=True)

                        else:
                            self.SendMessage(id, 'Некорректный л/с')
                            self.SendLinkToMain(id)
                    except:
                        self.SendMessage(id, 'Некорректный л/с!!!!')
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
                elif (session == 'Адреса пунктов обслуживания'):
                    Keyboard = ReplyKeyboardMarkup()
                    Keyboard.RemoveKeyboard(id)
                    if messagetext=='Кострома':
                        dataflow = ['Центральный пункт', 'Фабричный пункт']
                        Keyboard = ReplyKeyboardMarkup()
                        Keyboard.create(1, 2, dataflow)
                        responsetext = 'Выберите пункт обслуживания?'
                        Keyboard.SendKeyboard(id, responsetext)
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
                            self.SendLocation(id, latGPS, longGPS)
                        except ObjectDoesNotExist:
                            self.SendMessage(id, 'Не найден пункт обслуживания по указанным данным!!!')
                    self.SendLinkToMain(id)
                    self.Cleansession(id)

    def ExecInRNG(self,id,algname,params):
        datameterjson = ''
        try:
            if(UseTrains==False):
                RNG = RNGConnector()
                res = RNG.Connect()
                if(res!=False):
                    datameterjson = RNG.Execute(algname, JsonResponse(params, safe=False))
                else:
                    self.SendMessage(id,
                                     'В данный момент проводятся регламентные работы. Повторите попытку позже. Приносим извинения за доставленные неудобства.')
                    OopsEventsOfReq.objects.update_or_create(id=id,defaults={'id': id})
                    self.SendLinkToMain(id)
            else:
                RNG = TrainConnector(hosttrain,logintrains,passwordtrains)
                datameterjson = RNG.Execute(algname, JsonResponse(params, safe=False))
                if(datameterjson=="Error"):
                    self.SendMessage(id,
                                     'В данный момент проводятся регламентные работы. Повторите попытку позже. Приносим извинения за доставленные неудобства.')
                    OopsEventsOfReq.objects.update_or_create(id=id, defaults={'id': id})
                    self.SendLinkToMain(id)
        except:
            self.SendMessage(id,
                             'В данный момент проводятся регламентные работы. Повторите попытку позже. Приносим извинения за доставленные неудобства.')
            self.SendLinkToMain(id)
        return datameterjson

    def CreateTabMeter(self,text,readout):
        text = text+'<table border="1">'
        text = text + '<tr><th>Дата показания</th><th>Показание</th><th>Источник</th></tr>'
        for read in readout:
            text = text + '<tr><td>'+read['datereadstr']+'</td><td>'+read['read']+'</td><td>'+read['readsource']+'</td></tr>'
        return text

    def SOCRLP(self,text):
        return ' '.join(text.split())

    def Cleansession(self,id):
        sessionstr = sessionstate.objects.get(id=id)
        sessionstr.delete()

    def SendMessage(self,id, text,RemoveKeyboard=False):
        if(RemoveKeyboard==False):
            Message = structSendMessage(id, text,'')
            messagejson = JsonResponse(Message, safe=False)
            headers = {'content-type': 'application/json'}
            res = requests.post(hosttelegram + tokenTelegram + '/sendMessage', data=messagejson, headers=headers)
            if res.status_code == 200:
                return True
            else:
                return False
        else:
            Keyboard = ReplyKeyboardMarkup()
            return Keyboard.RemoveKeyboard(id,text)

    def SendLinkToMain(self,id):
        dataflow = ['Главное меню', 'Настройки']
        Keyboard = ReplyKeyboardMarkup()
        Keyboard.create(1, 2, dataflow)
        responsetext = 'Выберите действие?'
        Keyboard.SendKeyboard(id, responsetext)

    def SendDocument(self,id,file_id,ls,month,isnew = True):
        data = {'chat_id': id}
        if(isnew==True):
            files = {'document': open(file_id, 'rb')}
        else:
            files = {'document': file_id}
        r = requests.post(hosttelegram + tokenTelegram + '/sendDocument', data=data, files=files)
        data = json.loads(r.content)
        try:
            file_id = data['result']['document']['document']['file_id']
            Receipt.objects.update_or_create(chatid=id, ls=ls,month = month,file_id=file_id,defaults={'chatid': id, 'ls': ls, 'month': month, 'file_id': file_id})
        except:
            print ('Error')

    def SendMain(self,id):
        Keyboard = ReplyKeyboardMarkup()
        Keyboard.RemoveKeyboard(id)
        dataflow = ['Взаиморасчеты', 'Передать показания счетчика', 'Адреса пунктов обслуживания', 'Квитанция',
                    'История показаний ПУ', 'Настройки']
        Keyboard = ReplyKeyboardMarkup()
        Keyboard.create(2, 3, dataflow)
        responsetext = 'Выберите действие?'
        Keyboard.SendKeyboard(id, responsetext)

    def SendLocation(self,id,lat,long):
        Message = structLocation(id,lat,long)
        messagejson = JsonResponse(Message, safe=False)
        headers = {'content-type': 'application/json; charset=utf-8'}
        res = requests.post(hosttelegram + tokenTelegram + '/sendLocation', data=messagejson, headers=headers)
        if res.status_code == 200:
            return True
        else:
            return False


def structKeyboardButton(text):
    return {'text': text}

def structLocation(chat_id = '', latitude = 0,longitude=0):
    return {'chat_id': chat_id,'latitude': latitude,'longitude': longitude}

def structSendMessage(chat_id = '', text = ' ',reply_markup='',entities='',location=''):
    return {'chat_id': chat_id,'text': text,'reply_markup':reply_markup,'parse_mode':'HTML'}

def structRemoveMessage(chat_id = None, remove_keyboard = True):
    return {'chat_id': chat_id, 'remove_keyboard': remove_keyboard}

class ReplyKeyboardMarkup():
    dataKeyboard=''
    def create(self, numofline, numofrow, dataflow):
        listofrow = []
        listofline =[]
        i=0
        iall=0
        lenfl = len(dataflow)
        br=False
        while (i<numofline):
            if(br==True):
               break;
            j = 0
            listofrow = []
            while(j<numofrow):
                if(iall>lenfl-1):
                    break
                    br = True
                listofrow.append(structKeyboardButton(dataflow[iall]))
                j=j+1
                iall = iall + 1
            i=i+1
            listofline.append(listofrow)
        self.dataKeyboard = {'keyboard': listofline,'resize_keyboard':True}

    def SendKeyboard(self,id,text):
        Message = structSendMessage(id, text, self.dataKeyboard)
        headers = {'content-type': 'application/json; charset=utf-8'}
        messagejson = JsonResponse(Message, safe=False)
        res = requests.post(hosttelegram+tokenTelegram+'/sendMessage', data=messagejson,headers=headers)
        if res.status_code == 200:
           return True
        else:
            return False

    def RemoveKeyboard(self,id,text=''):
        Message = structSendMessage(id, text, structRemoveMessage(id))
        messagejson = JsonResponse(Message, safe=False)
        headers = {'content-type': 'application/json; charset=utf-8'}
        res = requests.post(hosttelegram + tokenTelegram + '/sendMessage', data=messagejson, headers=headers)
        if res.status_code == 200:
           return True
        else:
            return False


