import requests
import logging
import json
import pandas as pd
from datetime import datetime


logging.basicConfig( level=logging.DEBUG, filename='request.log')
arrayForm = {
        "ID":[],
        "UNIDAD":[],
        "ICCID":[],
        "IMEI":[]
    }


def requestApiWialon(peticion):
    resInfo = []
    if peticion == True:
        print('...............................Ejecutando API de Wialon...............................')
        data = {
            'params' : '{"token":"4ce2721753a2ba37492c16677e988dcd55A431A2F4B1553E845919C866BD03A85F427EFB","operateAs":"","appName":"","checkService":""}',
            'sid':  ''
        }
        re = requests.get('https://hst-api.wialon.com/wialon/ajax.html?svc=token/login&sid=',params=data)
        eid = re.json()['eid']
        dataInfo = {
            'params' : '{"spec":[{"type":"type","data":"avl_unit","flags":4294967295,"mode":0}]}',
            'sid':  eid
        }
        reqDatos = requests.get('https://hst-api.wialon.com/wialon/ajax.html?svc=core/update_data_flags&sid='+eid,params=dataInfo)
        resInfo = json.loads(reqDatos.text.encode(encoding='UTF-8'));
        
        print('...............................Guardando en json...............................')
        with open('request.json','w') as j:
            json.dump(resInfo, j)
    else:
        resInfo = leerJsonRequest()
    
    extraerTeltonikaFM130(resInfo=resInfo)
    extraerTeltonikaFM3612(resInfo=resInfo)
    #actualizarJsonPeticion(arrayForm)
    print('...............................Generando Excel ...............................')
    df = pd.DataFrame(arrayForm, columns = ['ID','UNIDAD', 'ICCID', 'IMEI'])
    now = datetime.today().strftime('%Y_%m_%d__%H_%M_%S')
    df.to_excel('docs/request_Teltonika_{}.xlsx'.format(now), sheet_name='datos')
    print('Total de GPS Teltonika encontrados: {}'.format(len(arrayForm['UNIDAD'])))
    
def extraerTeltonikaFM130(resInfo):
    print('.................. Iniando busqueda de los FMU130,FMU125,FMM130,FMC130,FMC125,FMB920,FMB130,FMB125,FMB120, .....................')
    arrayDatos = [];
    
    for p in range(len(resInfo)):
        if 'prms' in resInfo[p]['d'] and resInfo[p]['d']['prms'] != None:
            for iccid in resInfo[p]['d']['prms']:
                if iccid == 'iccid' :
                    arrayDatos.append(resInfo[p])
        
    for tel in range(len(arrayDatos)):
        arrayForm['ID'].append(str(arrayDatos[tel]['i']))
        arrayForm['UNIDAD'].append(str(arrayDatos[tel]['d']['nm']))
        arrayForm['ICCID'].append(arrayDatos[tel]['d']['prms']['iccid']['v'])
        arrayForm['IMEI'].append(arrayDatos[tel]['d']['uid'])
 
def extraerTeltonikaFM3612(resInfo):
    print('...............................Iniando busqueda de los FM3612...............................')
    arrayDatos = [];
    
    for p in range(len(resInfo)):
        if 'prms' in resInfo[p]['d'] and resInfo[p]['d']['prms'] != None:
            if 'adc3' in resInfo[p]['d']['prms'] and 'param14' in resInfo[p]['d']['prms']:
                arrayDatos.append(resInfo[p])
        
    for tel in range(len(arrayDatos)):
        ICCID = str(arrayDatos[tel]['d']['prms']['adc3']['v']).replace('.', '')+str(arrayDatos[tel]['d']['prms']['param14']['v'])
        if len(ICCID) > 9:
            arrayForm['ID'].append(str(arrayDatos[tel]['i']))
            arrayForm['UNIDAD'].append(str(arrayDatos[tel]['d']['nm']))
            arrayForm['ICCID'].append(ICCID)
            arrayForm['IMEI'].append(arrayDatos[tel]['d']['uid'])

def actualizarJsonPeticion(resInfo):
    print('............................... Actualizando json de peticion ...............................')
    objJson = leerJsonRequest()
    
    print('Datos iniciales: {}'.format(len(objJson)))
    posicion = 0
    while posicion < len(objJson):
        for gps in range(len(resInfo['ID'])):
            if int(resInfo['ID'][gps]) == int(objJson[posicion]['i']):
                objJson.pop(posicion)
                break
        posicion = posicion+1
                
    print('Datos finales: {}'.format(len(objJson)))
    
    with open('request.json','w') as j:
            json.dump(objJson, j)
    
def leerJsonRequest():
    print('............................... Extrayendo json de peticion ...............................')
    objJson = []
    with open('request.json','r') as j:
        objJson = json.load(j)
    return objJson

            
if __name__ == "__main__":
    requestApiWialon(peticion=True)