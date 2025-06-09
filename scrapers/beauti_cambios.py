#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import json
import os
import platform
import re
import time
from io import BytesIO

from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from upload import converToArcadj, capchaGoogle


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


total = []


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
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--headless')
        driver = webdriver.Chrome('./chromedriver', chrome_options=options)
        wait = WebDriverWait(driver, 10)

    def resolverCapcha():
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
        except:
            print("Fallo Capturando la capcha")
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
            return leearTablaBeauti(driver.page_source)
        except:
            nombres = driver.find_element_by_id('ctl00_cplPrincipal_lblAdministrado').text
            print(nombres)
            sinTablas = driver.find_element_by_id('ctl00_cplPrincipal_lblMensajeSinDatos').text
            print(sinTablas)
            driver.execute_script("window.history.go(-1)")
            return "Datos Vacios"

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

        paginasTotales = len(paginaF)

        if paginasTotales > 0:
            print("El Contribuynte tiene mas de 1 tabla")
            pt = 2
            while pt > paginasTotales:
                rows = table_body.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    l2 = ["lblAnio", "lblPeriodo", "lblDocumento", "lblDeuda", "lblPagado", "lblFecVen", "lblEstado", "imgAyuda", "lblEstadoDoc", "lblEstadoNot", "lblFecNot", "lblEstadoExp", "lblReferencia"]
                    diccionari = dict(zip(l2, [ele for ele in cols if ele]))
                    print(diccionari)
                    data.append(diccionari)

                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table/tbody/tr[12]/td/table/tbody/tr/td[{}]/a').__format__(paginasTotales))).click()
            print("data con mas de 1 tabla: {}".format(data))
        else:
            print("El Contribuynte solo tiene una tabla")
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                # data.append([ele for ele in cols if ele])  # Get rid of empty values
                # cols = [ele.text.strip() for ele in cols]
                l2 = ["lblAnio", "lblPeriodo", "lblDocumento", "lblDeuda", "lblPagado", "lblFecVen", "lblEstado", "imgAyuda", "lblEstadoDoc", "lblEstadoNot", "lblFecNot", "lblEstadoExp", "lblReferencia"]
                diccionari = dict(zip(l2, [ele for ele in cols if ele]))
                print(diccionari)
                data.append(diccionari)
            print("data con 1 sola tabla: {}".format(data))
        return data

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

        tabla = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table')))
        # tabla = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
        print("Verificando si existen contribuyentes")
        paginacion = tabla.find_elements(By.CLASS_NAME, "grillaRows")
        paginacion1 = tabla.find_elements(By.CLASS_NAME, "grillaAlternate")
        # print(type(paginacion))
        pagiTtoal = int(len(paginacion)) + int(len(paginacion1))
        print("Se encontraron {} Contribuyentes".format(pagiTtoal))

        # input("Cualquiertecla para continuar")

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
        return total

    else:
        print("Logica Paraeintentar capcha")
        # resolverCapcha()
        # pass

    # print(driver.page_source)
    # def leearTablarContribuyente(contribuyente, pagina):
    #     print("Inciando con el Contribuyente {}".format(contribuyente))
    #     print('/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a')
    #     wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a'))).click()
    #     try:
    #         wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
    #     finally:
    #         leearTablaBeauti(driver.page_source)

    # print(driver.page_source)

    def leerTablarPorUser(contribuyente):
        try:
            # print("Entrando a la funcion se ejecutara mientras que {} sea menor que {}".format(d, pagiTtoal))
            # tabla = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table')))
            # rows = tabla.find_elements(By.CLASS_NAME, "grillaRows")
            # rows2 = tabla.find_elements(By.CLASS_NAME, "grillaAlternate")
            # totalRow = int(len(rows)) + int(len(rows2)) + 2  # se suman 2 porque los arreglos inician en 0 mas la cabezera que no se cuenta
            # print("grillaRows: {}".format(len(rows)))
            # print("grillaAlternate: {}".format(len(rows2)))
            print("Inciando con el Contribuyente {}".format(contribuyente))
            print('/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a')
            wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[4]/div/div/table/tbody/tr[' + str(contribuyente) + ']/td[2]/a'))).click()
            # tablaNew = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table')))
            try:
                tablaNew = wait.until(EC.presence_of_element_located((By.ID, 'ctl00_cplPrincipal_grdEstadoCuenta')))
            except:
                # print()
                print("Datos Vacios")
                pass
            paginacionNew = tablaNew.find_elements(By.CLASS_NAME, "grillaPager")
            # print(type(paginacion))
            pagiTtoalNew = int(len(paginacionNew)) + int(1)
            print("Paginacion Segunda table {}".format(pagiTtoalNew))
            arcaDj = converToArcadj(driver.get_screenshot_as_base64())
            # driver.page_source
            dd = 0
            sdf = []
            while dd < pagiTtoalNew:
                # click a contribuyentes
                tabla2 = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table')))
                nombreContri = driver.find_element_by_xpath('/html/body/form/div[3]/section/div/div/div[2]/div[3]/div[2]/p/span').text
                print(nombreContri)
                driver.save_screenshot("tabla{}.png".format(dd))
                # Cuenos las columnas
                rows2 = tabla2.find_elements(By.CLASS_NAME, "AltRowStyle")
                rows22 = tabla2.find_elements(By.CLASS_NAME, "grillaAlternate")
                rows222 = tabla2.find_elements(By.CLASS_NAME, "grillaRows")
                # totalRow = int(len(rows2)) + int(len(rows22)) + int(len(rows222)) + 2 # se suman 2 porque los arreglos inician en 0 mas la cabezera que no se cuenta
                totalRow = int(len(rows2)) + int(len(rows22)) + int(len(rows222)) + 2  # se suman 2 porque los arreglos inician en 0 mas la cabezera que no se cuenta
                print("AltRowStyle: {}".format(len(rows2)))
                print("grillaAlternate: {}".format(len(rows22)))
                print("grillaRows: {}".format(len(rows222)))
                # print(dd)
                # cantidadde contribuyentes 0 es 1
                print("EL Segundo contador {}".format(dd))
                print("El total a recorrer por table {}".format(totalRow))
                # se define el numero 2 para que onicie con el año de la tabla y omita el checkbox
                recorrido = 2
                print("el whi se ejecuta si recorrido:{} es menor a {}".format(recorrido, totalRow))
                while recorrido < totalRow:
                    # recorrido de las columnas segun cantidad total
                    print('ctl00_cplPrincipal_grdEstadoCuenta_ctl0{}_lblAnio'.format(recorrido))
                    restante = recorrido / 10
                    restanteFormat = str(restante).replace('.', '')
                    # solo para valdiar que ya cargo la tabla
                    lblAnio = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblAnio'.format(restanteFormat)).text
                    lblPeriodo = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblPeriodo'.format(restanteFormat)).text
                    lblDocumento = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblDocumento'.format(restanteFormat)).text
                    lblDeuda = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblDeuda'.format(restanteFormat)).text
                    lblPagado = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblPagado'.format(restanteFormat)).text
                    lblFecVen = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblFecVen'.format(restanteFormat)).text
                    lblEstado = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblEstado'.format(restanteFormat)).text
                    imgAyuda = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblEstado'.format(restanteFormat)).text
                    lblEstadoDoc = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblEstadoDoc'.format(restanteFormat)).text
                    lblEstadoNot = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblEstadoNot'.format(restanteFormat)).text
                    lblFecNot = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblFecNot'.format(restanteFormat)).text
                    lblEstadoExp = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblEstadoExp'.format(restanteFormat)).text
                    lblReferencia = driver.find_element_by_id('ctl00_cplPrincipal_grdEstadoCuenta_ctl{}_lblReferencia'.format(restanteFormat)).text

                    jsonResult = {
                        "lblAnio": lblAnio,
                        "lblPeriodo": lblPeriodo,
                        "lblDocumento": lblDocumento,
                        "lblDeuda": lblDeuda,
                        "lblPagado": lblPagado,
                        "lblFecVen": lblFecVen,
                        "lblEstado": lblEstado,
                        "imgAyuda": imgAyuda,
                        "lblEstadoDoc": lblEstadoDoc,
                        "lblEstadoNot": lblEstadoNot,
                        "lblFecNot": lblFecNot,
                        "lblEstadoExp": lblEstadoExp,
                        "lblReferencia": lblReferencia
                    }
                    # print(jsonResult)
                    sdf.append(jsonResult)
                    recorrido = recorrido + 1

                print("el sdf pusheado {}".format(sdf))
                jsonFinal = {
                    "nombres": formatearNombre(nombreContri),
                    "codRes": "00",
                    "impuestos": sdf,
                    "codigoArchivo": arcaDj
                }
                # Al finalizar click a la pagina siguiente
                print("##############Termino de leer la tabla y pusheando a totales ####################")
                total.append(jsonFinal)
                # time.sleep(2)
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/section/div/div/div[2]/div[7]/div/div/div/div/table/tbody/tr[12]/td/table/tbody/tr/td[2]/a'))).click()
                    time.sleep(2)
                except:
                    # print(NameError)
                    print("NO HAY BOTON DE SIGUINTE PAGINA")
                dd = dd + 1

            print("EL TOTALLLLLLLLLL - 0 {}".format(total))
            print("Ir atras12")
            print("Datos Vacios")
            driver.execute_script("window.history.go(-1)")
            print("EL TOTALLLLLLLLLL - 1 {}".format(total))

        except:
            print("Ir atras1")
            print("Datos Vacios")
            # print(NameError)
            driver.execute_script("window.history.go(-1)")

    # return "No se encontro registros"
    # print("EL TOTALLLLLLLLLL - 3 {}".format(total))


"""
    p = 2
    print("el while se va aejecutarmientras {} sea menor-igual que {}".format(p, pagiTtoal))
    while p <= pagiTtoal + 1:
        leerTablarPorUser(p)
        print("while")
        print(p)
        p = p + 1
    print("Siempre seejecuta esto")
    driver.quit()
    return total
"""

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
