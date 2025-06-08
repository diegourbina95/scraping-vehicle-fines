
from pymongo import MongoClient
import os
from bson.json_util import dumps, loads

mongo = MongoClient(os.getenv("URL_MONGO"))

db  = mongo.get_database("db")
def BuscarUltimoRegistro(coleccion, condition):
    col = db[coleccion]
    resultado = col.find(condition).sort("_id", -1).limit(1)
    if resultado.count() > 0:
        jsonResp = resultado[0]
        jsonResp['_id'] = str(jsonResp['_id'])
        return dumps(jsonResp)
    else:
        return "null"


def buscarMongoOne(valor, parametro , coleccion):
    col = db[coleccion]
    id =col.find_one({parametro: valor})
    return id

def insertarMongo(valor, coleccion):
    col = db[coleccion]
    id =col.insert_one(valor)
    return id

def deletearMongo(valor, parametro, coleccion):
    col = db[coleccion]
    id =col.delete_one({parametro: valor})
    return id