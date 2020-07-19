import requests
import time
import re
import urllib3
import json
from datetime import datetime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


config = {
    "smsbalance": xxx,
    "numtosend": "xxx",
    "fromsender": "xxx",
    "accountapi": "xxx",
    "loginapi": "xxx",
    "passwordapi": "xxx"
}


headers = {
    "api_key": "ba0c2dad52b3ec",
    "X-LBC-CC": "5",
    "Accept": "application/json,application/hal+json",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "api.leboncoin.fr",
    "Connection": "Keep-Alive",
    "User-Agent": "LBC;Android;9;Chrome/80.0.3987.119;phone;874c06eec2dbd1c8;wifi;4.55.3.0;95300;0"
}

# your json data here
data = {}


def initList():
    liste = []
    try:
        page = requests.post(str('https://api.leboncoin.fr/api/adfinder/v1/search'), verify=False, headers=headers, json=data)
        response = page.json()
        for a in response['ads'] :
            liste.append(int(a['list_id']))   
    except Exception as e : 
        print(e)
    return liste
    
def sendMsg(paramMsg):
    responseLog = ""
    finalMsg = "Annonce(s) : %0d {} %0dReste : {}".format(paramMsg[0],  paramMsg[1]['smsbalance'] - len(paramMsg[1]['numtosend'].split(",")))
    msgSended = False
    try :
        #je pourrais utiliser config directement ici mais vu que j'aime pas la porté des variables en python...
        sending = requests.get(str('https://www.ovh.com/cgi-bin/sms/http2sms.cgi?&account={}&login={}&password={}&from={}&to={}&message={}&noStop=1&contentType=application/json'.format(paramMsg[1]['accountapi'],paramMsg[1]['loginapi'],paramMsg[1]['passwordapi'],paramMsg[1]['fromsender'],paramMsg[1]['numtosend'],finalMsg)))
        if sending.status_code == 200 :
            responseLog = finalMsg.replace("%0d", "\n")
            msgSended = True
        else : 
            responseLog = "Erreur d'envoie des sms : {} \n".format(str(sending.status_code))
    except Exception as e :
        responseLog = "Pas de réponse {} \n".format(str(e))
    f = open("send.txt", "a")
    f.write("Envoyer le {} \n{}\n".format(str(datetime.now()), responseLog))
    f.close()
    return msgSended



needNotif = False
liste = initList()
paramMsg = []
txtMsg = ""


while True :
    time.sleep(600)
    responseLog = ""
    try :
        page = requests.post(str('https://api.leboncoin.fr/api/adfinder/v1/search'), verify=False, headers=headers, json=data)
        response = page.json()
        newListe = []
        responseLog = str(response['total'])
        for a in response['ads'] :
            newListe.append(int(a['list_id']))
            if a['list_id'] not in liste:
                txtMsg += "{}{}".format(a['url'],"%0d")
                needNotif = True
        if needNotif == True :
            paramMsg.append(txtMsg)
            paramMsg.append(config)
            if  txtMsg != "" and sendMsg(paramMsg): #comparaison paraisseuse 
                liste = newListe
                config['smsbalance'] -= len(config['numtosend'].split(","))
                needNotif = False
            # traitement du cas ou l'envoi d'un message a echoué et que l'annonce a été del entre temps
            # si txtmsg n'est pas reset risque à la fin de de ce bloc risque de doublons en cas de fail d'envoi
            if txtMsg == "": 
                needNotif = False
            txtMsg = ""
    except Exception as e : 
        responseLog = str(e)
    f = open("passage.txt", "a")
    f.write("Passage à {} : \n{} \n".format(str(datetime.now()), responseLog))
    f.close()



