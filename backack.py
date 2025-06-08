#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import os
import platform
import re
from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from upload import capchaGoogle


def formatearNombre(nombre):
    # Creando patron e busqueda
    patron = re.compile(r'\W+')
    # Limpiando nombre y eliminando espacion
    palabras = patron.split(nombre)
    str1 = ' '.join(str(e) for e in palabras)
    # print(str1)
    return str1


def get_as_base64(url):
    image = open(url, 'rb')  # open binary file in read mode
    image_read = image.read()
    image_64_encode = base64.encodestring(image_read)
    ### de bytes a string
    to_string = image_64_encode.decode("utf-8")
    return to_string

    # cookies = cPickle.load(open("cookies.pkl", "rb"))
    # for cookie in cookies:
    #     driver.add_cookie(cookie)
    # # return urlopen(url, "filename.png")
    # driver.get(url)
    # asd = base64.b64encode(requests.get(url).content)
    # print(asd)



def impuestoVehicular(placa):
    SysOs = platform.system()
    print(SysOs)
    if SysOs == "Windows":
        path = os.getcwd() + "\\"
        # print('Directorio raiz: {}'.format(path))
        # Chrome session Windows
        options = webdriver.ChromeOptions()
        # options.add_argument("--force-dev-mode-highlighting")
        # options.add_argument("--disable-extensions")
        # options.add_argument("--disable-features=EnableEphemeralFlashPermission")
        # options.add_argument('--headless')
        driver = webdriver.Chrome(chrome_options=options)
        wait = WebDriverWait(driver, 10)
    else:
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        driver = webdriver.Chrome('./chromedriver', chrome_options=options)
        wait = WebDriverWait(driver, 10)

    def resolverCapcha():
        print("Ejecutando la resolucion de capcha")
        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'captcha_class')))
            # time.sleep(10)
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
            im.save('screenshot.png', optimize=True, quality=95)  # saves new cropped image
            base64capcha = get_as_base64('screenshot.png')
            result = capchaGoogle(base64capcha)
            jsonParse = json.loads(result)['responses'][0]['textAnnotations'][1]['description']
            return jsonParse
        except NameError:
            print("Fallo Capturando la capcha")
            print(NameError)
            pass

    def leearTablacontribuyente(contribuyente, paginas):
        print("Inciando con el Contribuyente {}".format(contribuyente))
        # print('/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a')
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a'))).click()
        try:
            print("El Contribuyente tiene data")
            wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
            nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
            print("Procesando el contribuyente {}".format(nombres))
            jsonFinal = {
                "nombres": nombres,
                "codRes": "00",
                "impuestos": leearTablaBeauti(driver.page_source),
                "codigoArchivo": "123123123"
            }
            return jsonFinal
        except:
            nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
            print("Procesando el contribuyente {}".format(nombres))
            sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
            print("Respuesta de la lectura de la table {}".format(sinTablas))
            driver.execute_script("window.history.go(-1)")
            jsonFinal = {
                "nombres": nombres,
                "codRes": "01",
                "impuestos": [],
                "codigoArchivo": "123123123"
            }
            return jsonFinal

    def leearTablaBeauti(html):
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
        table_body = table.find('tbody')

        paginacion = table_body.find_all('tr', attrs={'class': 'grillaPager'})
        for row in paginacion:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            paginaF.append([ele for ele in cols if ele])  # Get rid of empty values
        print("Cantidad de pagina del contribuyente: {}".format(paginaF))

        def RecolectarDatos():
            print("#####################")
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                # print([ele for ele in cols])
                l2 = ["id","anio", "cuota", "documentoCodigoPago", "totalDeuda", "pagado", "vencimiento", "estado", "estadoDocDeuda", "estadoDocNotificado", "fechaNotificacion", "estadoExpediente", "referencia"]
                diccionari = dict(zip(l2, [ele for ele in cols]))
                print(diccionari)
                data.append(diccionari)
            return [item for item in data if len(item)>0]

        paginasTotales = len(paginaF)
        result_reco = []
        if paginasTotales > 0:
            print("El Contribuynte tiene mas de 1 tabla")
            pt = 2
            while pt > paginasTotales:
                result_reco = RecolectarDatos()
                print("Aqui se imprime el recorrido de las paginas cuand se tiene mas de contribuyentes {}".format(result_reco))
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table/tbody/tr[12]/td/table/tbody/tr/td[{}]/a').__format__(paginasTotales))).click()
            print("data con mas de 1 tabla: {}".format(data))
            return result_reco
        else:
            print("El Contribuynte solo tiene una tabla")
            result_reco = RecolectarDatos()
            print("El Contribuynte solo tiene una tabla {}".format(result_reco))
            return result_reco

    print("Inicio ejecucion")
    driver.get("https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx")
    # wait.until(EC.UrlContains('https://www.sat.gob.pe/WebSitev8/IncioOV2.aspx'))

    driver.switch_to.frame(driver.find_element_by_name("fraRightFrame"))
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/div[2]/nav/div/div/ul/li[2]/a'))).click()
    """
    wait.until(EC.presence_of_element_located((By.XPATH, ''))).click()
    wait.until(EC.presence_of_element_located((By.NAME, ''))).click()
    wait.until(EC.presence_of_element_located((By.ID, ''))).click()
    """
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[2]/div[2]/nav/div/div/ul/li[2]/ul/li[1]/a'))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[2]/div/select/option[6]'))).click()
    except:
        print("Error Cargarndo la web de IV")
        return "Error Cargarndo la web de IV"

    # wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtPlaca'))).send_keys("B0V507")
    # wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtPlaca'))).send_keys("D8L108")
    wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtPlaca'))).send_keys(str(placa))
    print("Iniciando resoluciona de capcha")

    jsonParseCapcha = resolverCapcha()
    if (len(jsonParseCapcha)) == 4:
        wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtCaptcha'))).send_keys(str(jsonParseCapcha))
        # driver.find_element_by_name("ctl00$cplPrincipal$txtCaptcha").send_keys(str(jsonParse))
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[3]/div[6]/div/div[3]/div[2]/input'))).click()
        # driver.find_element_by_xpath("/html/body/form/div[3]/section/div/div/div[2]/div[5]/div/div[3]/div[2]/input").click()
        try:
            tabla = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table')))
        except:
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[2]/div/select/option[6]'))).click()
            wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtPlaca'))).send_keys(str(placa))
            print("Iniciando resoluciona de capcha")
        # tabla = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
        print("Verificando si existen contribuyentes")
        paginacion = tabla.find_elements(By.CLASS_NAME, "grillaRows")
        paginacion1 = tabla.find_elements(By.CLASS_NAME, "grillaAlternate")
        # print(type(paginacion))
        pagiTtoal = int(len(paginacion)) + int(len(paginacion1))
        print("Se encontraron {} Contribuyentes".format(pagiTtoal))

        # input("Cualquiertecla para continuar")
        total = []
        print("Aqui Inicia la logica por contribuyente")
        p = 2
        print("el while se ejecutar mientras que {} sea menor-igual que {}".format(p, pagiTtoal))
        while p <= pagiTtoal + 1:
            sad = leearTablacontribuyente(p, "null")
            print("Respuesta de la funcion final {}".format(sad))
            total.append(sad)
            print("Procesado el contribuyente {}".format(p))
            p = p + 1
        print("Fin del Scrappers")
        driver.quit()
        print(total)
        return total

    else:
        wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[2]/div/select/option[6]'))).click()
        wait.until(EC.presence_of_element_located((By.NAME, 'ctl00$cplPrincipal$txtPlaca'))).send_keys(str(placa))
        print("Iniciando resoluciona de capcha")
        print("Logica Paraeintentar capcha")
        # resolverCapcha()
        # pass

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
