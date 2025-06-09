import json
import os
import random
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
# x = 1
# while x < 12:
#     restante = x / 10
#     restanteFormat = str(restante).replace('.', '')
#     print(restanteFormat)
#     x = x + 1
#
# import re
#
# txt = "1.0"
# x = re.search("^The.*Spain$", txt)
# print(x)
try:
    getter = requests.get('https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx')
    print(getter)
except Exception:
    print("Web Caida")
    print(Exception)

# asd = [{'1015923 porras patiño margot aydee'}]
# qwe = len(asd)
# for r in asd:
#     print(type(r))
#     print(r)

# miLista=['F0=000201', 'F1=GSM02', 'F2=00', 'F3=43F3D8', 'F4=08910480', 'F5=1', 'F6=24435656', 'F7=192462848093', 'F9=0', 'F10=20150106', 'F11=113215', 'F12=113220', 'F13=000005', 'F14=000000', 'F15=000012', 'F16=0']
#
# miLista= [element.split('=') for element in miLista]
# miDiccionario = dict((key,value) for key,value in miLista )
# print(miDiccionario)
print(randomString(10))

# array = {'nombres': '1030426 - VILLAREAL JACOBO, JULIO VICTOR', 'codRes': '01', 'impuestos': [], 'codigoArchivo': '123123123'}
# asd = json.loads(array)
# print(asd)

import re
from unicodedata import normalize

def Normalizar(s):
    # -> NFD y eliminar diacríticos
    s = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", normalize( "NFD", s), 0, re.I)
    # -> NFC
    s = normalize( 'NFC', s)
    # print( s )
    return s

s = "Pingüino: Málãgà ês uñ̺ã cíudãd fantástica y èn Logroño me pica el... moñǫ̝̘̦̞̟̩̐̏̋͌́ͬ̚͡õ̪͓͍̦̓ơ̤̺̬̯͂̌͐͐͟o͎͈̳̠̼̫͂̊"
print(Normalizar(s))


import unicodedata

s = 'aepáéŕíóíúÁÉ'
def Normalizacion(s):
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    s = unicodedata.normalize('NFKC', unicodedata.normalize('NFKD', s).translate(trans_tab))
    return s


driver = webdriver.Remote(
    desired_capabilities=webdriver.DesiredCapabilities.CHROME,
    command_executor=os.getenv('WEBDRIVER')
)
driver.get('http://saucelabs.com/test/guinea-pig')
print(driver.page_source)
driver.quit()