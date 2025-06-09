from pymongo import MongoClient
import os
import logging

client = MongoClient()
logging.debug("Mongo Conectado a: {}".format("mongodb://10.3.3.122:27017"))
mongo = MongoClient("mongodb://10.3.3.122:27017")

class MongoConect(object):
	def __init__(self, arg):
		self.arg = arg

	def InsertarMongoLima(self):
		print("self.arg")
		print(self.arg)
		print(type(self.arg))
		print("self.arg")
		id = mongo.db.Lima.insert_one(self.arg)
		logging.debug("Seguardo correctamente")
		return id


jsonss = {
	"codRes": "00",
	"codigoArchivo": 2437572,
	"detalles": [
		{
			"carrito": "carrito",
			"id": "",
			"placa": "D8L109",
			"reglamento": "SET",
			"falta": "R19",
			"documentoCodigoPago": "C1658607",
			"fechaInfracEmision": "20/03/2019",
			"importe": "86.00",
			"gastCost": "0.00",
			"dscto": "43.00",
			"totalPagar": "43.00",
			"estado": "Pendiente",
			"licenciaConducir": "Q07905577"
		},
		{
			"carrito": "carrito",
			"id": "",
			"placa": "D8L109",
			"reglamento": "RNT",
			"falta": "G57",
			"documentoCodigoPago": "12700741",
			"fechaInfracEmision": "29/10/2018",
			"importe": "344.00",
			"gastCost": "81.80",
			"dscto": "0.00",
			"totalPagar": "425.80",
			"estado": "EnCoactiva",
			"licenciaConducir": "Q07905577"
		}
	],
	"importeTotal": 430.0,
	"placa": "D8L109"
}

asd = MongoConect(jsonss)
asd.InsertarMongoLima()