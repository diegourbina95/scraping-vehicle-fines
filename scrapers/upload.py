import base64
import os
import requests
import json
import logging

path = os.getcwd() + "/screen/"


# logging.debug('Directorio raiz: {}'.format(path))

def unirImagen(arreglosArcas):
    logging.debug("Uniendo Imagenes")
    logging.debug(arreglosArcas)
    myobj = {
        "unirImg": [
            arreglosArcas
        ]
    }
    print(myobj)
    logging.debug(myobj)
    x = requests.post(os.getenv('UNIRIMAGEN'), data=myobj)
    # x = requests.post("http://127.0.0.1:7654/unirImg", data=myobj)
    print(x)
    logging.debug(x.text)
    result_parseado = json.loads(x.content)
    logging.debug(result_parseado['codigoArchivo'])
    return result_parseado['codigoArchivo']


def converToArcadj(directorio):
    try:
        print("subiendo archivo")
        return 0
        # logging.debug(directorio)
        # variable = 'data:image/png;base64,' + directorios
        # print("cargando....")
        # logging.debug(variable)
        # myobj = {'base': variable}
        # print("generando arcadj")
        # x = requests.post(os.getenv('URL_BASE64'), data=myobj)
        # logging.debug(x.text)
        # result_parseado = json.loads(x.content)
        # logging.debug(result_parseado['co_archiv'])
        # print(result_parseado['co_archiv'])
        # return result_parseado['co_archiv']
        
    except NameError:
        print(NameError)


def capchaGoogle(base64):
    # importing the requests library
    import requests
    # data to be sent to api
    data = {
        "requests": [
            {
                "image": {
                    "content": base64
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION",
                        "maxResults": 1
                    }
                ]
            }
        ]
    }
    # logging.debug(data)

    # sending post request and saving response as response object
    r = requests.post(url=os.getenv('API_ENDPOINT'), data=json.dumps(data))

    # extracting response text
    pastebin_url = r.text
    # logging.debug("The pastebin URL is:%s"%pastebin_url)
    return pastebin_url

# capchaGoogle()
# print(unirImagen([2437517, 2437518]))
