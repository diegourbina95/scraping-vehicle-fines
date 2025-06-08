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
from upload import capchaGoogle, converToArcadj, unirImagen
from anticaptchaofficial.recaptchav2proxyless import *
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

def impuestoVehicularv2(placa, webdrivertipo):
    try:
        # getter = requests.get('https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx')
        # print(getter)
        SysOs = platform.system()
        print(SysOs)
        path = os.getcwd() + "\\"
        # print('Directorio raiz: {}'.format(path))

        # Chrome session Windows
        # options = webdriver.ChromeOptions()
        # options.add_argument("--force-dev-mode-highlighting")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-features=EnableEphemeralFlashPermission")
        # options.add_argument('--headless')
        # driver = webdriver.Chrome(chrome_options=options)
        # driver.set_window_position(0, 0)
        try:
            driver = webdriver.Remote(
                desired_capabilities=webdriver.DesiredCapabilities.CHROME,
                command_executor=webdrivertipo
            )
            # driver.set_window_size(1920, 1580)
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
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[3]/div[6]/div/div[3]/div[2]/input'))).click()
                time.sleep(5)
                # driver.save_screenshot("/tmp/prueba-despuesdelclick.png")
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
            arcasUnidas = []
            def leearTablaBeauti(html):
                result_reco = []

                def ordenarRespuesta():
                    return "Se encontraton {} arreglos y es: {}".format(len(result_reco), result_reco)

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
                def RecolectarDatos(html):
                    arcasUnidas.append(converToArcadj(driver.get_screenshot_as_base64()))
                    soup = BeautifulSoup(html, 'lxml')
                    data = []
                    paginaF = []

                    # nombreContri = soup.find_all('ctl00_cplPrincipal_lblAdministrado')
                    # print(nombreContri.text)

                    table = soup.find('table', attrs={'id': 'ctl00_cplPrincipal_grdEstadoCuenta'})
                    # arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                    table_body = table.find('tbody')
                    # print("#####################")
                    rows = table_body.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        cols = [ele.text.strip() for ele in cols]
                        print([ele for ele in cols])
                        l2 = ["anio", "cuota", "documentoCodigoPago", "totalDeuda", "dsctoOficSat", "desctoWebBancos", "pagado", "deudaOficSat", "deudaWebBancos", "vencimiento", "estado", "estadoDocNotificado", "estadoDocDeuda", "fechaNotificacion", "estadoExpediente", "referencia"]
                        diccionari = dict(zip(l2, [ele for ele in cols]))
                        # print(diccionari)
                        data.append(diccionari)
                    return [item for item in data if len(item) > 0]

                paginasTotales = len(paginaF)
                print("PAGINAS POR RECORRER {}".format(paginasTotales))
                if paginasTotales > 0:
                    print("El Contribuynte tiene mas de 1 tabla")
                    print("pt es 2 <= {}".format(paginasTotales))
                    pt = 2
                    # arcasDjs = []
                    while pt <= paginasTotales + 2:
                        print("Ejecutando PT = {}".format(pt))
                        # print(driver.page_source)
                        result_reco.append(RecolectarDatos(driver.page_source))
                        print("Aqui se imprime el recorrido de las paginas cuand se tiene mas de contribuyentes {}".format(result_reco))
                        # print('/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table/tbody/tr[12]/td/table/tbody/tr/td[{}]/a'.format(pt))
                        try:
                            # arcasDjs.append(converToArcadj(driver.get_screenshot_as_base64()))
                            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table/tbody/tr[12]/td/table/tbody/tr/td[{}]/a'.format(pt)))).click()
                            time.sleep(5)
                            # print(driver.page_source)
                            print("Este el valor de PT: {}".format(pt))
                            pt = pt + 1
                        except:
                            print("Entro el EXCEPT")
                            # print("data con mas de 1 tabla: {}".format(result_reco))
                            # pt = pt + 1
                            print(ordenarRespuesta())
                            return result_reco
                        # yield result_reco
                    # arcasUnidas.append(unirImagen(arcasDjs))
                    # return result_reco
                else:
                    print("El Contribuynte solo tiene una tabla")
                    result_reco = RecolectarDatos(driver.page_source)
                    # print("El Contribuynte solo tiene una tabla {}".format(result_reco))
                    print(ordenarRespuesta())
                    return result_reco



            print("Inciando con el Contribuyente {}".format(contribuyente))
            # print('/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a')
            try:
                wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a'))).click()
                time.sleep(5)
                print("El Contribuyente tiene data")
                try:
                    espero = WebDriverWait(driver, 4)
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
                        print("existe la tabla - este")
                        nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
                        print("Procesando el contribuyente {}".format(nombres))
                        # arcaDj = converToArcadj(driver.get_screenshot_as_base64())

                        print("arcadj generado")
                        # def asd(qwe):
                        #     if len(qwe) == 0:
                        #         arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        #         print(arcaDj)
                        #         return arcaDj
                        #     else:
                        #         return arcasUnidas[0]


#                         # driver.save_screenshot(path + "prueba.png")
#                         jsonFinal = {
#                             "nombres": nombres,
#                             "codRes": "00",
#                             "impuestos": leearTablaBeauti(driver.page_source),
#                             "codigoArchivo": unirImagen(arcasUnidas)
#                         }
                        jsonFinal = {
                            "nombres": nombres,
                            "codRes": "00",
                            "impuestos": leearTablaBeauti(driver.page_source),
                            "codigoArchivo": arcasUnidas[0]
                        }
                        print("{}".format(jsonFinal))
                        return jsonFinal

                    else:
                        # print("ENTRO AL ELSEEEEEEEEEEEEEEEE")
                        # sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
                        # print("Respuesta de la lectura de la table {}".format(sinTablas))
                        # arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        print(arcaDj)
                        driver.execute_script("window.history.go(-1)")
                        jsonFinal = {
                            "nombres": "null",
                            "codRes": "01",
                            "impuestos": [],
                            "codigoArchivo": arcaDj
                        }
                        return jsonFinal
                except:
                    try:
                        print("ENTRO AL EXEOPppppppppppppp")
                        # sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
                        # print("Respuesta de la lectura de la table {}".format(sinTablas))
                        wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
                        nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
                        print("Procesando el contribuyente {}".format(nombres))
                        arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        # arcaDj = converToArcadj(driver.get_screenshot_as_base64())
                        print(arcaDj)
#                         # driver.save_screenshot(path + "prueba.png")
                        jsonFinal = {
                            "nombres": nombres,
                            "codRes": "00",
                            "impuestos": leearTablaBeauti(driver.page_source),
                            "codigoArchivo": arcaDj
                        }
                        driver.quit()
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




        def leerCapcha(driver):
            sitekey = driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute('data-sitekey')
            print(sitekey)
            getKeyResolv = resolvCapcha(sitekey)
            container = driver.find_element_by_id("g-recaptcha-response")
            driver.execute_script("arguments[0].style.display = 'block';", container)
            print("executinh ")
            driver.execute_script("arguments[0].style.margin = '18px 149px';", container)
            driver.execute_script(
                "document.getElementById('g-recaptcha-response').innerHTML='{}'".format(getKeyResolv))
            print("ANTES DE VALIDAR")
            # driver.execute_script("validarCaptcha();")
            print("SE EJECUTO")


        def resolvCapcha(sitekey):
            solver = recaptchaV2Proxyless()
            solver.set_verbose(1)
            solver.set_key(os.getenv('KEY_ANTICAPTCHA'))
            solver.set_website_url(
                "https://www.sat.gob.pe/pagosenlinea/")
            solver.set_website_key(str(sitekey))
            g_response = solver.solve_and_return_solution()
            if g_response != 0:
                print("g-response: " + g_response)
                return g_response
            else:
                print("task finished with error " + solver.error_code)
                return solver.error_code

        print("Inicio ejecucion")
        # driver.implicitly_wait(10)  # seconds
        driver.get("https://www.sat.gob.pe/pagosenlinea/")
        # print(test)
        print("Ya paso el get")
        # myDynamicElement = driver.find_element_by_name("fraRightFrame")

        # wait.until(EC.UrlContains('https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx'))

       
     
        try:
            # wait.until(EC.presence_of_element_located((By.ID, 'strTipDoc'))).click()
            # time.sleep(2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="strTipDoc"]/option[3]'))).click()
            time.sleep(2)
        except:
            print("Error Cargarndo la web de IV")
            return "Error Cargarndo la web de IV"

        wait.until(EC.presence_of_element_located((By.ID, 'strNumDoc'))).clear()
        wait.until(EC.presence_of_element_located((By.ID, 'strNumDoc'))).send_keys(str(placa))
        print("Iniciando resoluciona de capcha")
        leerCapcha(driver)

        print("fin cparcha")
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/form[1]/div[3]/div[1]/div[2]/div[5]/div/button'))).click()
        # 
        # t = 0

        try:
            print("")
            time.sleep(4)
            driver.find_element(By.ID, "btnPopup_Aceptar")
            print("EXISTE EL BOTON NO HAY DATA DE LA PLACA")
            try:
                texttt = driver.find_element(By.XPATH, "/html/body/div[1]/form[1]/div[4]/div/div/div[2]").text
                if texttt == "Verificación incorrecta. Por favor, verifique o seleccione control Re-Captcha.":
                    return {"codRes":"99"}
            except:
                pass

            response = {
                "codRes":"01",
                "placa":placa,
                "codigoArchivo": converToArcadj(driver.get_screenshot_as_base64()),
                "created_at": datetime.now(),
                "impuestoVehicular":{
                    "montoTotal":"-"
                }, 
                "papeletas":{
                    "montoTotal":"-"
                }
            }
            driver.quit()
            return response 
            # 
        except:
            print("")
            monto1 = ""
            monto2 = ""
            try:
                texto1 = driver.find_element(By.XPATH, '//*[@id="divImpVehicular"]/div/div[1]').text
                print("texto1", texto1.splitlines())
                monto1 = texto1.splitlines()[1].split(":")[1].strip()
            except:
                pass

            try:
                texto2 = driver.find_element(By.XPATH, '//*[@id="divPapeletas"]/div/div[1]').text
                print("texto2", texto2.splitlines())
                monto2 = texto2.splitlines()[1].split(":")[1].strip()
            except:
                pass
                
            data =  {
                "codRes":"00",
                "placa":placa,
                "impuestoVehicular":{
                    "montoTotal":monto1,
                },
                "codigoArchivo": converToArcadj(driver.get_screenshot_as_base64()),
                "created_at": datetime.now(),
                "papeletas":{
                    "montoTotal":monto2
                }

            }
            driver.quit()
            return data
            # 
        # while t < 3:
            # # jsonParseCapcha = resolverCapcha()
            # print("Respuesta apCcha {}".format(jsonParseCapcha))
            # print(len(jsonParseCapcha))
            # print(type(len(jsonParseCapcha)))

            # total = []
            # if len(jsonParseCapcha) == 1:
            #     print("Cargando table de contribuyente")
            #     # total = []
            #     print("Aqui Inicia la logica por contribuyente")
            #     p = 2
            #     print("el while se ejecutar mientras que {} sea menor-igual que {}".format(p, jsonParseCapcha))
            #     while p <= int(jsonParseCapcha) + 1:
            #         sad = leearTablacontribuyente(p, "null")
            #         print("Respuesta de la funcion final {}".format(sad))
            #         total.append(sad)
            #         print("Procesado el contribuyente {}".format(p))
            #         p = p + 1
            #     print("Fin del Scrappers")
            #     driver.quit()
            #     print(total)
            #     return total
            #     # t = 3
            # else:
        
            #     # time.sleep(2)
            #     pass
    except Exception as e:
        print("Web Caida", e)
# leearTablarContribuyente
# 1 solo contri 2 tablas
# impuestoVehicular("ADB466")
# 1 solo contri sin datos
# impuestoVehicular("D8L108")
# 2 contri sin datos
# impuestoVehicular("D9R252")


# 2 contri sin datos
# impuestoVehicular("B0V507")
# 1 contri con 3 datos
# impuestoVehicular("BBC618")
