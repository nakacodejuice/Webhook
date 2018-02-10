from zeep import Client
import json
import requests
from django.http import JsonResponse

WSDLRNG = 'http://h044-svc-04/RNG_EGS/ws/dataexchange.1cws?wsdl'
loginRNG = ""
passRNG = ""

class RNGConnector():
    ClientSOAP = "";
    def Connect(self):
        try:
            ClientSOAP = Client(WSDLRNG)
            result = self.Execute("Тест соединения","")
            return True
        except:
            return False

    def Execute(self,algname,parametrsjson):
        try:
            resultjson = self.ClientSOAP.service.ВыполнитьАлгоритмИПолучитьРезультат(algname, parametrsjson)
            received_json_data = json.loads(resultjson.decode("utf-8-sig"))
            return received_json_data
        except:
            return False


