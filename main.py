# -*- coding: utf-8 -*-
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path  # python3 only

from bson.json_util import dumps, loads
from dotenv import load_dotenv
from flask import request, jsonify
from pymongo import MongoClient

import conexionesMongo
import test_untitled
import test_untitledmasivo
from app import app
from iv import impuestoVehicular
from ivVersion2 import impuestoVehicularv2
from ivmasivo import impuestoVehicularmasivo
from tributos import multasTribu
from IV_FOR_DOCUMENTO import IV_FOR_DOCUMENTO
from bd.mongo import BuscarUltimoRegistro, buscarMongoOne, insertarMongo, deletearMongo
import limaDoc

client = MongoClient()
logging.debug("Mongo Conectado a: {}".format(os.getenv("URL_MONGO")))
mongo = MongoClient(os.getenv("URL_MONGO"))


def diferenviaDias(fecha):
    print(type(fecha))
    # fecha = fecha.datetime.strftime("%Y-%m-%d")
    dateTimeObj = datetime.now()
    fecha = fecha.strftime("%d-%b-%Y %H:%M:%S.%f")
    hoy = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S.%f")
    d1 = datetime.strptime(fecha, '%d-%b-%Y %H:%M:%S.%f')
    d2 = datetime.strptime(hoy, '%d-%b-%Y %H:%M:%S.%f')
    diff = (d2 - d1).days
    return diff


def InsertarMongo(valor):
    id = mongo.db.impuestoV.insert_one(valor)
    logging.debug("Seguardo correctamente")
    return id

def InsertarMongov2(valor):
    id = mongo.db.impuestoVehicularv2.insert_one(valor)
    logging.debug("Seguardo correctamente")
    return id


def InsertarMongoMasivo(valor):
    id = mongo.db.impuestoVmasivo.insert_one(valor)
    logging.debug("Seguardo correctamente")
    return id


def InsertarMongoIVD(valor):
    id = mongo.db.IVDocumento.insert_one(valor)
    logging.debug("Seguardo correctamente")
    return id.inserted_id


def InsertarMongoLima(valor):
    print(valor)
    id = mongo.db.Lima.insert_one(valor)
    logging.debug("Seguardo correctamente")
    return id


def DeleteMongo(placa):
    # resultplaca = mongo.impuestoV.deleteOne({"placa" : placa})
    mongo.db.impuestoV.delete_one({"placa": placa})
    response = {
        "detalle": "Se elimino la placa correctamente"
    }
    return response


def DeleteMongoLima(placa):
    # resultplaca = mongo.impuestoV.deleteOne({"placa" : placa})
    id=mongo.db.Lima.delete_one({"placa": placa})
    return id

def DeleteMongoIVD(placa):
    # resultplaca = mongo.impuestoV.deleteOne({"placa" : placa})
    mongo.db.IVDocumento.delete_one({"documento": placa})
    response = {
        "detalle": "Se elimino la placa correctamente"
    }
    return response


def BuscarMongo(placa):
    resultplaca = mongo.db.impuestoV.find_one({"placa": placa})
    resp = dumps(resultplaca)
    return resp


def BuscarMongomasivo(placa):
    resultplaca = mongo.db.impuestoV.find({
        "placa": placa,
        "created_at": {"$gte": datetime.now() - timedelta(days=10)}
    })
    resp = dumps(resultplaca)
    return resp

def BuscarMongoMasivoLIMA(placa):
    resultplaca = mongo.db.Lima.find_one({"placa": placa})
    resp = dumps(resultplaca)
    return resp


def DeleteMongoMasivoLIMA(placa):
    # resultplaca = mongo.impuestoV.deleteOne({"placa" : placa})
    mongo.db.Lima.delete_one({"placa": placa})
    response = {
        "detalle": "Se elimino la placa correctamente"
    }
    return response



def InsertarMongoMasivoLima(valor):
    print(valor)
    id = mongo.db.Lima.insert_one(valor)
    logging.debug("Seguardo correctamente")
    return id


def BuscarMongoIVD(placa):
    resultplaca = mongo.db.IVDocumento.find_one({"documento": placa})

    resp = dumps(resultplaca)
    return resp


def BuscarMongoLima(placa):
    resultplaca = mongo.db.impuestoV.find_one({"placa": placa})
    resp = dumps(resultplaca)
    return resp


def ActualizarMongo(placa):
    resultplaca = mongo.db.impuestoV.find_one({"placa": placa})
    resp = dumps(resultplaca)
    return resp


# Test
@app.route('/impuesto/delete/<placa>', methods=['GET'])
def delete(placa):
    test = DeleteMongo(placa)
    return test


@app.route('/impuesto/find/<tipo>', methods=['GET', 'POST'])
def find(tipo):
    logging.debug("buscando {}".format(tipo))
    test = BuscarMongo(tipo)
    return test


# Home apge
@app.route('/', methods=['GET'])
def home_page():
    return json.dumps('Scrapper Impuesto Vehicular')


# Nuevo 2020-11
@app.route('/multast/<int:tipo>', methods=['POST'])
def multast(tipo):
    logging.debug(tipo)
    if tipo == 1:
        if request.method == 'POST':
            json = request.get_json()
            result = multasTribu(str(json['dni']))
            logging.debug(result)
            jsonResponse = {
                "codRes": "01",
                "dni": json['dni'].upper(),
                "detalles": result
            }
            return jsonResponse
    elif tipo == 2:
        if request.method == 'POST':
            try:
                json = request.get_json()
                return json
            except NameError:
                jsonResponse = {
                    "codRes": "01",
                    "placa": json['placa'].upper(),
                    "detalles": "null",
                    "propietario": "null",
                    "resultPropietario": "null"
                }
                logging.debug("aqui va el nuevo response {}".format(jsonResponse))
                logging.debug(NameError)
                # InsertarMongo(jsonResponse)
                return jsonResponse
    else:
        return 'Tipo incorrecto'
        # return todas(json_forma)


# Nuevo 2020-11
@app.route('/ivdocumento/<int:tipo>', methods=['POST'])
def ivdocumento(tipo):
    logging.debug(tipo)
    # BuscarMongoIVD()
    if tipo == 1:
        try:
            if request.method == 'POST':
                json = request.get_json()
                buscar = BuscarMongoIVD(json['documento'].upper())
                getFecha = loads(buscar)
                print(getFecha)
                global created
                try:
                    created = diferenviaDias(getFecha['created_at'])
                except:
                    created = 4

                if buscar == "null" or created > 3:
                    DeleteMongoIVD(str(json['documento']).upper())
                    result = IV_FOR_DOCUMENTO(str(json['documento']), str(json['tipoDocumento']))
                    resultType = type(result)
                    logging.debug(resultType)
                    logging.debug(result)
                    print("result", result)
                    if result != None:
                        # logging.debug(len(result))
                        # logging.debug(result)
                        jsonResponse = {
                            "codRes": "00",
                            "documento": json['documento'].upper(),
                            "detalles": result,
                            "created_at": datetime.now()
                        }
                        InsertarMongoIVD(jsonResponse)
                        print(jsonResponse)
                        jsonResponse['_id'] = str(jsonResponse['_id'])
                        # print(type(jsonResponse))
                        return {**jsonResponse}
                    else:
                        jsonResponse = {
                            "codRes": "99",
                            "documento": json['documento'].upper(),
                            "detalles": "null",
                            "created_at": datetime.now()
                        }
                        return jsonResponse
                else:
                    logging.debug("Respuesta del Mongo:")
                    logging.debug(buscar)
                    return buscar
        except:
            jsonResponse = {
                "codRes": "99",
                "documento": json['documento'].upper(),
                "detalles": "null",
                "created_at": datetime.now()
            }
            return jsonResponse


    elif tipo == 2:
        if request.method == 'POST':
            try:
                json = request.get_json()
                DeleteMongoIVD(json["documento"])
                return json
            except:
                pass


@app.route('/impuestovehicular/<int:tipo>', methods=['POST'])
def multas(tipo):
    logging.debug(tipo)
    if tipo == 1:
        if request.method == 'POST':
            try:
                json = request.get_json()
                # buscar = BuscarMongomasivo(json['placa'].upper())
                # print("-----buscarbuscar------>", buscar, len(buscar), type(buscar))
                # if buscar != "[]": 
                #     buscar = loads(buscar)[0]
                # print("<------------------------>", buscar)
                ip = json.get('ip', 'defecto')
                webdrivertipo = ''
                if ip == "defecto":
                    webdrivertipo = os.getenv('WEBDRIVER')
                else:
                    busqueda =  buscarMongoOne("00", "codRes" ,"catalogo_ips") 
                    print("busquedA", busqueda)
                    try:
                        webdrivertipo = "http://{}:4444/wd/hub".format(busqueda['ips'][int(ip)-1])
                    except:
                        print("ERROR, NO SE ABRIO CON AWS")
                        webdrivertipo = os.getenv('WEBDRIVER')
                        
                # buscar = BuscarUltimoRegistro("impuestoV", { "placa": json['placa'].upper()})
                buscar = None
                # getFecha = loads(buscar)
                # print(getFecha)
                # global created
                
                try:
                    created = diferenviaDias(getFecha['created_at'])
                except:
                    created = 6      
                if buscar == "null" or created > 5:
                    print("SCRAPING")
                    result = impuestoVehicular(str(json['placa']).upper(), webdrivertipo)
                    print(result)
                    resultType = type(result)
                    logging.debug(resultType)
                    logging.debug(result)
                    logging.debug(len(result))

                    # logging.debug(result[0])
                    # logging.debug(result[1])
                    def validar(valor):
                        if valor > 0:
                            return '00'
                        else:
                            return '01'

                    codigoRespuesta = []
                    respArcadj = []
                    x = 0
                    while x < len(result):
                        respuesta = result[x]['codRes']
                        if respuesta == '00':
                            codigoRespuesta.append(result[x]['codRes'])
                        else:
                            pass
                        respArcadj.append(result[x]['codigoArchivo'])
                        x = x + 1

                    if len(result) <= 0:
                        response = {
                            "codRes": validar(len(codigoRespuesta)),
                            "placa": json['placa'].upper(),
                            "contribuyentes": "Datos Vacios",
                            "codigoArchivo": respArcadj[0],
                            "codigoArchivoUrl": os.getenv('codigoArchivoUrl').format(respArcadj[0]),
                            "created_at": datetime.now()
                        }
                        InsertarMongo(response)
                        logging.debug(response)
                        logging.debug(type(response))
                        return dumps(response)
                    else:
                        response = {
                            "codRes": validar(len(codigoRespuesta)),
                            "placa": json['placa'].upper(),
                            "contribuyentes": result,
                            "codigoArchivo": respArcadj[0],
                            "codigoArchivoUrl": os.getenv('codigoArchivoUrl').format(respArcadj[0]),
                            "created_at": datetime.now()
                        }
                        InsertarMongo(response)
                        logging.debug(response)
                        logging.debug(type(response))
                        return dumps(response)
                        # logging.debug(result)
                        # return result
                else:
                    print(buscar)
                    return buscar
            except:
                response = {
                    "codRes": "99",
                    "placa": json['placa'].upper(),
                    "contribuyentes": "null",
                    "codigoArchivo": "null"
                }
                #                 # InsertarMongo(response)
                return dumps(response)
    elif tipo == 2:
        if request.method == 'POST':
            try:
                json = request.get_json()
                return json
            except NameError:
                jsonResponse = {
                    "codRes": "01",
                    "placa": json['placa'].upper(),
                    "detalles": "null",
                    "propietario": "null",
                    "resultPropietario": "null"
                }
                logging.debug("aqui va el nuevo response {}".format(jsonResponse))
                logging.debug(NameError)
                # InsertarMongo(jsonResponse)
                return jsonResponse
    else:
        return 'Tipo incorrecto'
        # return todas(json_forma)



@app.route('/impuestovehicular/v2/<int:tipo>', methods=['POST'])
def impuestovehicularv2(tipo):
    logging.debug(tipo)
    if tipo == 1:
        if request.method == 'POST':
            try:
                json = request.get_json()
                ip = json.get('ip', 'defecto')
                webdrivertipo = ''
                if ip == "defecto":
                    webdrivertipo = os.getenv('webdriver')
                else:
                    busqueda =  buscarMongoOne("00", "codRes" ,"catalogo_ips") 
                    print("busquedA", busqueda)
                    try:
                        webdrivertipo = "http://{}:4444/wd/hub".format(busqueda['ips'][int(ip)-1])
                    except:
                        print("ERROR, NO SE ABRIO CON AWS")
                        webdrivertipo = os.getenv('webdriver')
                        
                # buscar = BuscarUltimoRegistro("impuestoVehicularv2", { "placa": json['placa'].upper()})
                buscar = None
                # getFecha = loads(buscar)
                # print(getFecha)
                # global created
                
                try:
                    created = diferenviaDias(getFecha['created_at'])
                except:
                    created = 6      
                if buscar == "null" or created > 5:
                    result = impuestoVehicularv2(str(json['placa']).upper(), webdrivertipo)
                    print(result)
                    resultType = type(result)
                    logging.debug(resultType)
                    logging.debug(result)
                    logging.debug(len(result))
                    InsertarMongov2(result)
                    return dumps(result)
                else:
                    print(buscar)
                    return buscar
            except:
                response = {
                    "codRes": "99",
                    "placa": json['placa'].upper(),
                    "contribuyentes": "null",
                    "codigoArchivo": "null"
                }
                #                 # InsertarMongo(response)
                return dumps(response)
    elif tipo == 2:
        if request.method == 'POST':
            try:
                json = request.get_json()
                return json
            except NameError:
                jsonResponse = {
                    "codRes": "01",
                    "placa": json['placa'].upper(),
                    "detalles": "null",
                    "propietario": "null",
                    "resultPropietario": "null"
                }
                logging.debug("aqui va el nuevo response {}".format(jsonResponse))
                logging.debug(NameError)
                # InsertarMongo(jsonResponse)
                return jsonResponse
    else:
        return 'Tipo incorrecto'
        # return todas(json_forma)







@app.route('/ms/scrappers/v2.0/papeletas/lima', methods=['POST'])
def multasLima():
    try:
        json = request.get_json()
        ip = json.get('ip', 'defecto')
        print("Ip enviado", ip)
        webdrivertipo = ''
        if ip == "defecto":
            webdrivertipo = os.getenv('WEBDRIVER')
        else:
            busqueda =  buscarMongoOne("00", "codRes" ,"catalogo_ips") 
            print("busquedA", busqueda)
            try:
                webdrivertipo = "http://{}:4444/wd/hub".format(busqueda['ips'][int(ip)-1])
            except:
                print("ERROR, NO SE ABRIO CON AWS")
                webdrivertipo = os.getenv('WEBDRIVER')
        

        # print("buscar", ip)
        # buscar = BuscarUltimoRegistro("Lima", { "placa": json['placa'].upper()})
        # print("sssssss", buscar)
        # getFecha = loads(buscar)
        # print(getFecha)
        # global created

        buscar = None
        
        try:
            created = diferenviaDias(getFecha['created_at'])
        except:
            created = 6      
        if buscar == "null" or created > 5:
            print("EN EL BUSCAR")
            scrap = test_untitled.TestUntitled(str(json['placa']).upper(), webdrivertipo)
            result = scrap.test_untitled()
            print("result")
            print(result)
            print("result")
            # insertarMongo = conexionesMongo.MongoConect(result)
            # asd = insertarMongo.InsertarMongoLima()
            # print(asd)
            return dumps(result)
        else:
            print(buscar)
            return buscar
    except:
        resultado = {
            "codRes": "99",
            "placa": json['placa'],
            "detalles": [],
            "importeTotal": 0,
            "codigoArchivo": ""
        }
        cerrar = test_untitled.TestUntitled(resultado)
        cerrar.teardown_method()
        return dumps(resultado)





@app.route('/ms/scrappers/v2.0/papeletas/lima/documento', methods=['POST'])
def multasLimaDoc():
    try:
        json = request.get_json()
        ip = json.get('ip', 'defecto')
        webdrivertipo = ''
        if ip == "defecto":
            webdrivertipo = os.getenv('WEBDRIVER')
        else:
            busqueda =  buscarMongoOne("00", "codRes" ,"catalogo_ips") 
            try:
                webdrivertipo = "http://{}:4444/wd/hub".format(busqueda['ips'][int(ip)-1])
            except:
                print("ERROR, NO SE ABRIO CON AWS")
                webdrivertipo = os.getenv('WEBDRIVER')
        resultadoMongo = BuscarUltimoRegistro('LimaDocumento', { "documento": json['documento']})
        print("resultadoMongo", resultadoMongo)
        getFecha = loads(resultadoMongo)
        print(getFecha)
        global created
        try:
            created = diferenviaDias(getFecha['created_at'])
        except:
            created = 6      
        print(created)
        if resultadoMongo == "null" or created > 5:
            print("<---------------------->|", json['documento'])
            scrap = limaDoc.TestUntitled(str(json['documento']), webdrivertipo)
            result = scrap.test_untitled()
            print("result")
            print(result)
            print("result")
            insertarMongo(result, 'LimaDocumento' )
            return dumps(result)
        else:
            return resultadoMongo
    except:
        resultado = {
            "codRes": "99",
            "documento": json['documento'],
            "detalles": [],
            "importeTotal": 0,
            "codigoArchivo": ""
        }
        # cerrar = test_untitled.TestUntitled(resultado)
        # cerrar.teardown_method()
        return dumps(resultado)


try:
    enviro = sys.argv[1]
    if enviro == "dev":
        env_path = Path('.') / '.env.dev'
        load_dotenv(dotenv_path=env_path)
        logging.debug(os.getenv('ENVIRO'))
    if enviro == "pro":
        env_path = Path('.') / '.env.pro'
        load_dotenv(dotenv_path=env_path)
        logging.debug(os.getenv('ENVIRO'))
    if __name__ == '__main__':
        # app.run()
        app.run(host='0.0.0.0', port="4567", debug=True)
except:
    logging.debug("Debe definir el entorno dev o pro (ejm: python app.py dev)")
    # logging.debug(NameError)
