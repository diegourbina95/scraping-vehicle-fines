#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import random
import string
import json
import os
import platform
import requests
import re
from io import BytesIO, StringIO
import time
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from upload import capchaGoogle, converToArcadj

def formatearNombre(nombre):
    # Creando patron e busqueda
    patron = re.compile(r'\W+')
    # Limpiando nombre y eliminando espacion
    palabras = patron.split(nombre)
    str1 = ' '.join(str(e) for e in palabras)
    # print(str1)
    return str1

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def get_as_base64(url):
    image = open(url, 'rb')  # open binary file in read mode
    image_read = image.read()
    image_64_encode = base64.encodestring(image_read)
    ### de bytes a string
    to_string = image_64_encode.decode("utf-8")
    return to_string

# Nuevo 2020-11
def multasTribu(dni):
    print("Entro en multas")
    try:
        SysOs = platform.system()
        print(SysOs)
        path = os.getcwd() + "\\"
        try:
            driver = webdriver.Remote(
                desired_capabilities=webdriver.DesiredCapabilities.CHROME,
                command_executor=os.getenv('webdriver')
            )
        except:
            return "No se puede acceder a la web"
        wait = WebDriverWait(driver, 10)

        def resolverCapcha():
            print("Ejecutando la resolucion de capcha")
            try:
                time.sleep(1)
                element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'captcha_class')))
                # element = driver.find_element_by_class_name('captcha_class')  # find part of the page you want image of
                location = element.location
                size = element.size
                png = driver.get_screenshot_as_png()  # saves screenshot of entire page
                im = Image.open(BytesIO(png))  # uses PIL library to open image in memory
                left = location['x']
                top = location['y']
                right = location['x'] + size['width']
                bottom = location['y'] + size['height']
                im = im.crop((left, top, right, bottom))  # defines crop points
                if SysOs == "Windows":
                    im.save('screenshot.png', optimize=True, quality=100)  # saves new cropped image
                    base64capcha = get_as_base64('screenshot.png')
                else:
                    name = randomString(10)
                    print(name)
                    # driver.save_screenshot("/tmp/prueba-enlacapcha.png")
                    im.save('/tmp/screenshot.png', optimize=True, quality=100)  # saves new cropped image
                    base64capcha = get_as_base64('/tmp/screenshot.png')
                result = capchaGoogle(base64capcha)
                jsonParse = json.loads(result)['responses'][0]['textAnnotations'][1]['description']
                print(jsonParse)
                wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtCaptcha'))).clear()
                wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtCaptcha'))).send_keys(str("{}".format(jsonParse)))
                time.sleep(5)
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[3]/div[5]/div/div[3]/div[2]/input'))).click()
                # driver.save_screenshot("/tmp/prueba-despuesdelclick.png")
                print(driver.current_url)
                try:
                    espero = WebDriverWait(driver, 2)
                    # espero.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[2]/div/select/option[6]')))
                    espero.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[2]/div/select/option[6]'))).click()
                    time.sleep(5)
                    print("reintentar capcha")
                    return "False"
                finally:
                    espero = WebDriverWait(driver, 2)
                    tabla = espero.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table')))
                    print("Leyendo tabla...")
                    print("Verificando si existen contribuyentes")
                    paginacion = tabla.find_elements(By.CLASS_NAME, "grillaRows")
                    paginacion1 = tabla.find_elements(By.CLASS_NAME, "grillaAlternate")
                    pagiTtoal = int(len(paginacion)) + int(len(paginacion1))
                    print("Se encontraron {} Contribuyentes".format(pagiTtoal))
                    return str(pagiTtoal)

            except:
                try:
                    # driver.save_screenshot("/tmp/prueba-leersin datos.png")
                    # sinContribuyente = wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/form/div[3]/section/div/div/div[2]/div[5]/div/p/span'))).text
                    # print(len(sinContribuyente))
                    # print("Sin contri {}".format(sinContribuyente))
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[5]/div/p/span')))
                    # arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                    # print("ARCADJ CONVERTIDO {}".format(arcaDj))
                    # return str(arcaDj)
                    return str("1234567")

                except:
                    # print(NameError)
                    print("Fallo Capturando la capcha")
                    return "False"

        def leearTablacontribuyente(contribuyente, paginas):
            # Recorrer table siempre que encuentre logica aplicada mas a abajo
            def leearTablaBeauti(html):
                print("Iniciando lectura de la tabla")

                # print("{}".format(html))
                """
                <a href="javascript:__doPostBack('ctl00$cplPrincipal$grdEstadoCuenta','Page$2')">2</a>
                <a href="javascript:__doPostBack('ctl00$cplPrincipal$grdEstadoCuenta','Page$1')">1</a>
                """
                soup = BeautifulSoup(html, 'lxml')
                data = []
                paginaF = []

                # nombreContri = soup.find_all('ctl00_cplPrincipal_lblAdministrado')
                # print(nombreContri.text)

                table = soup.find('table', attrs={'id': 'ctl00_cplPrincipal_grdEstadoCuenta'})
                # arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                table_body = table.find('tbody')
                print("Leyendo tabla principal")

                try:
                    # print("ENTRPA TRUYYYYYYYYYYYYYYYYYYYYYY")
                    paginacion = table_body.find_all('tr', attrs={'class': 'grillaPager'})
                    print("PAGIANSASASAAS {}".format(paginacion))
                    for row in paginacion:
                        print("Lineas por paginas {}".format(row))
                        cols = row.find_all('td')
                        cols = [ele.text.strip() for ele in cols]
                        paginaF.append([ele for ele in cols if ele])  # Get rid of empty values
                    # print("Cantidad de pagina del contribuyente: {}".format(paginaF[0]))
                except NameError:
                    print("No tiene paginas")
                    print(NameError)
                print("Paso la lectura de paginacion")
                def RecolectarDatos():
                    # print("#####################")
                    rows = table_body.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        cols = [ele.text.strip() for ele in cols]
                        # print([ele for ele in cols])
                        l2 = ["id", "anio", "cuota", "documentoCodigoPago", "totalDeuda", "pagado", "vencimiento", "estado", "estadoDocDeuda", "estadoDocNotificado", "fechaNotificacion", "estadoExpediente", "referencia"]
                        diccionari = dict(zip(l2, [ele for ele in cols]))
                        print(diccionari)
                        data.append(diccionari)
                    return [item for item in data if len(item) > 0]

                paginasTotales = len(paginaF)
                print("PAGINAS POR RECORRER {}".format(paginasTotales))
                if paginasTotales > 0:
                    print("El Contribuynte tiene mas de 1 tabla")
                    print("pt es 2 <= {}".format(paginasTotales))
                    pt = 2
                    result_reco = []
                    while pt <= paginasTotales + 1:
                        print("Ejecutando PT = {}".format(pt))
                        result_reco.append(RecolectarDatos())
                        print("Aqui se imprime el recorrido de las paginas cuand se tiene mas de contribuyentes {}".format(result_reco))
                        print('/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table/tbody/tr[12]/td/table/tbody/tr/td[{}]/a'.format(pt))
                        try:
                            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table/tbody/tr[12]/td/table/tbody/tr/td[{}]/a'.format(pt)))).click()
                            time.sleep(5)
                            pt = pt + 1
                        except:
                            print("data con mas de 1 tabla: {}".format(result_reco))
                            # pt = pt + 1
                            return result_reco[1]
                        # yield result_reco

                else:
                    print("El Contribuynte solo tiene una tabla")
                    result_reco = RecolectarDatos()
                    print("El Contribuynte solo tiene una tabla {}".format(result_reco))
                    return result_reco

            print("Inciando con el Contribuyente {}".format(contribuyente))
            try:
                time.sleep(4)
                # Entrar al detalle del contribuyente
                print("click al Contribuyente")
                wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a'))).click()
                try:
                    # Validando si el contribuyente tiene datos, para eso leo el campo de detalle ctl00_cplPrincipal_lblMensajeSinDatos y si tiene caracteres es que si existe si no tiene existe pero oculto sin datos
                    espero = WebDriverWait(driver, 2)
                    mensaje = espero.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_lblMensajeSinDatos'))).text
                    print("Mensaje NUevpo: {}".format(mensaje))
                    print("Caracters {}".format(len(mensaje)))
                    print(type(len(mensaje)))
                    if len(mensaje) == 0:
                        # print("ENTRO AL IFFFFFFFFFFF")
                        # nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
                        # print("Procesando el contribuyente {}".format(nombres))
                        # sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
                        # print("Respuesta de la lectura de la table {}".format(sinTablas))
                        # arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
                        print("existe la tabla")
                        nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
                        print("Procesando el contribuyente {}".format(nombres))
                        arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        print("arcadj generado")
#                         # driver.save_screenshot(path + "prueba.png")
                        jsonFinal = {
                            "nombres": nombres,
                            "codRes": "00",
                            "impuestos": leearTablaBeauti(driver.page_source),
                            "codigoArchivo": arcaDj
                        }
                        print("{}".format(jsonFinal))
                        return jsonFinal
                    else:
                        # print("ENTRO AL ELSEEEEEEEEEEEEEEEE")
                        # sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
                        # print("Respuesta de la lectura de la table {}".format(sinTablas))
                        arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        driver.execute_script("window.history.go(-1)")
                        jsonFinal = {
                            "nombres": "null",
                            "codRes": "01",
                            "impuestos": [],
                            "codigoArchivo": arcaDj
                        }
                        return jsonFinal
                except:
                    # Aqui entra cuando si tiene tabla (data)
                    try:
                        # print("ENTRO AL EXEOPppppppppppppp")
                        # sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
                        # print("Respuesta de la lectura de la table {}".format(sinTablas))
                        wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
                        nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
                        print("Procesando el contribuyente {}".format(nombres))
                        arcaDj = converToArcadj(driver.get_screenshot_as_base64())
#                         # driver.save_screenshot(path + "prueba.png")
                        jsonFinal = {
                            "nombres": nombres,
                            "codRes": "00",
                            "impuestos": leearTablaBeauti(driver.page_source),
                            "codigoArchivo": arcaDj
                        }
                        return jsonFinal
                    except NameError:
                        print(NameError)

            except:
                # print(NameError)
                # print("AQUI ESTA????????????????")
                # nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
                # print("Procesando el contribuyente {}".format(nombres))
                # sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
                # print("Respuesta de la lectura de la table {}".format(sinTablas))
                # arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                driver.execute_script("window.history.go(-1)")
                jsonFinal = {
                    "nombres": "null",
                    "codRes": "01",
                    "impuestos": [],
                    "codigoArchivo": arcaDj
                }
                return jsonFinal

        print("Inicio ejecucion")
        # driver.implicitly_wait(10)  # seconds
        driver.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")
        # print(test)
        print("Ya paso el get")
        # myDynamicElement = driver.find_element_by_name("fraRightFrame")

        # wait.until(EC.UrlContains('https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx'))

        driver.switch_to.frame(driver.find_element_by_name("fraRightFrame"))
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/div[2]/nav/div/div/ul/li[2]/a'))).click()
        time.sleep(5)
        """
        wait.until(EC.presence_of_element_located((By.XPATH, ''))).click()
        time.sleep(5)
        wait.until(EC.presence_of_element_located((By.NAME, ''))).click()
        time.sleep(5)
        wait.until(EC.presence_of_element_located((By.ID, ''))).click()
        time.sleep(5)
        """
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/div[2]/nav/div/div/ul/li[2]/ul/li[5]/a'))).click()
            time.sleep(2)
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[2]/div/select/option[3]'))).click()
            # time.sleep(3)
        except:
            print("Error Cargarndo la web de IV")
            return "Error Cargarndo la web de IV"

        wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtDocumento'))).clear()
        wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtDocumento'))).send_keys(str(dni))
        print("Iniciando resoluciona de capcha")

        t = 0
        while t < 3:
            jsonParseCapcha = resolverCapcha()
            print("Respuesta apCcha {}".format(jsonParseCapcha))
            print(len(jsonParseCapcha))
            print(type(len(jsonParseCapcha)))

            total = []
            if len(jsonParseCapcha) == 1:
                print("Cargando table de contribuyente")
                # total = []
                print("Aqui Inicia la logica por contribuyente")
                p = 2
                print("el while se ejecutar mientras que {} sea menor-igual que {}".format(p, jsonParseCapcha))
                while p <= int(jsonParseCapcha) + 1:
                    sad = leearTablacontribuyente(p, "null")
                    print("Respuesta de la funcion final {}".format(sad))
                    total.append(sad)
                    print("Procesado el contribuyente {}".format(p))
                    p = p + 1
                print("Fin del Scrappers")
                driver.quit()
                print(total)
                return total
                # t = 3
            else:
                if len(jsonParseCapcha) == 7:
                    sad = leearTablacontribuyente(2, "null")
                    print("Respuesta de la funcion final {}".format(sad))
                    total.append(sad)
                    # print("Procesado el contribuyente {}".format(2))
                    # driver.quit()
                    print(total)
                    # t = 5
                    return total
                    driver.quit()

                else:
                    # driver.save_screenshot("/tmp/prueba-.png")
                    # wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[2]/div/select/option[6]'))).click()
                    time.sleep(5)
                    wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtDocumento'))).clear()
                    wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtDocumento'))).send_keys(str(dni))
                    print("Logica Paraeintentar capcha N°: {}".format(t))
                    t = t + 1
                # time.sleep(2)
                # pass
    except:
        print("Web Caida")
# leearTablarContribuyente
# 1 solo contri 2 tablas
# multasTribu("45454545")
# 1 solo contri sin datos
# impuestoVehicular("D8L108")
# 2 contri sin datos
# impuestoVehicular("D9R252")


# 2 contri sin datos
# impuestoVehicular("B0V507")
# 1 contri con 3 datos
# impuestoVehicular("BBC618")
