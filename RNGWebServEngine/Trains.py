import json
import requests
from django.http import JsonResponse
from requests.auth import HTTPBasicAuth

class TrainConnector():
    def __init__(self,hosttrain,login,password):
        self.hosttrain =hosttrain
        self.login=login
        self.password=password
    def Execute(self,algname,parametrsjson):
        try:
            Message = {'event':'SetNewRequest','data':{'id':algname,'params':parametrsjson}};
            messagejson = JsonResponse(Message, safe=False)
            headers = {'content-type': 'application/json; charset=utf-8'}
            res = requests.post(self.hosttrain  + '/rest', data=messagejson, headers=headers, auth=HTTPBasicAuth(self.login, self.password))
            if (res.status_code == 200) and (res!="Timeout"):
                return "Error"
            else:
                return res
        except:
            return "Error"
