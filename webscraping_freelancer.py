# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.error import HTTPError
import bs4
from bs4 import BeautifulSoup
import requests
from controller import Controller
from configuration import FREELANCER
import unicodedata
from datetime import date
from datetime import datetime

from datetime import date
from datetime import datetime
from datetime import timedelta

def contain_br(contents):
    for element in contents:
        if type(element) is bs4.element.Tag:
            if element.name == "br":
                return True
    return False


def get_content(contents):
    lista = []
    for element in contents:
        if type(element) is bs4.element.NavigableString:
            if str(element) is not None and str(element).strip() != "":
                lista.append(str(element))
    return lista


def scraping_ofertas(con, url_principal, prefix_url, sufix_url, pagina_inicial, cant_paginas, cant_ofertas, id_carga):
    controller = Controller()
    lista_oferta = []       
    i=1
    m=0  

    obtener_lista_keywords(con)
    
    j=1
    #for i in range(pagina_inicial, cant_paginas):
    for i in range(FREELANCER["WS_PAGINA_INICIAL"], FREELANCER["WS_PAGINAS"]+1):
        #print(prefix_url)
        url_pagina = prefix_url + str(i) + sufix_url
        #print("------------------for i in range(pagina_inicial, cant_paginas)-------------------")
        print(url_pagina)

        req = requests.get(url_pagina)
        soup = BeautifulSoup(req.text, "lxml")
        try:
            
            avisos=soup.findAll("div", attrs={"class":"JobSearchCard-item-inner"})       
            #avisos=soup.findAll("div", attrs={"class":"row result click"})   
            print(len(avisos))                         
        except:
            avisos=[]
        

        #print(avisos)
        lista_oferta = []
        for el in avisos:
            
            print(j)
            j = j+1
            oferta = {}    
            href = el.find("a")['href']
            link = "http://www.freelancer.com.pe" + href
            #print("link: "+link)
            
            oferta["id_carga"] = id_carga
            # Almacena la url de la pagina
            oferta["url_pagina"] = url_pagina
            #print("URL_PAGINA "+ oferta["url_pagina"])
            # Almacena la url de la oferta
            oferta["url"] = link
            #print("URL: "+oferta["url"])

            redundancia  = controller.evitar_redundancia(con, oferta)
            #redundancia = None
            if(redundancia is None and oferta["url"].count("/login?") == 0):
                print("Registro nuevo")

                #----------------------------------------------------------------------------------------------------
                try:
                    oferta["time_publicacion"] = elimina_tildes(el.find("span", attrs={"class": "JobSearchCard-primary-heading-days"}).get_text().strip())
                except:
                    oferta["time_publicacion"] = "No detallado"

                #print("time_publicacion: "+ oferta["time_publicacion"])

                #----------------------------------------------------------------------------------------------------
                oferta["fecha_publicacion"] = datetime.now()
                #print(oferta["fecha_publicacion"])
                
                #----------------------------------------------------------------------------------------------------
                
                try:
                    oferta["puesto"] = elimina_tildes(el.find("a", {"class": "JobSearchCard-primary-heading-link"}).get_text().strip()[0:200])
                
                except:
                    oferta["puesto"] = "No detallado"

                #print("puesto: "+oferta["puesto"])

                
                #----------------------------------------------------------------------------------------------------
                try:
                    oferta["salario"] = elimina_tildes(el.find("div", {"class": "JobSearchCard-secondary-price"}).get_text().strip()[0:61])
                    oferta["salario"] = oferta["salario"].strip()
                except:
                    oferta["salario"] = "No detallado"

                #print("salario: "+oferta["salario"])
                #----------------------------------------------------------------------------------------------------
                
                oferta["empresa"] = "No detallado"
                #print("empresa: "+oferta["empresa"])
                
                

                #----------------------------------------------------------------------------------------------------
                
                # Accede al contenido HTML del detalle de la oferta
                reqDeta = requests.get(oferta["url"])            
                soup_deta = BeautifulSoup(reqDeta.text, "lxml")

                #----------------------------------------------------------------------------------------------------
                oferta["area"]="No detallado"
                #print("area: "+oferta["area"])

                #----------------------------------------------------------------------------------------------------
                oferta_d = soup_deta.find("div", attrs={"class":"PageProjectViewLogout-detail"})

                #------------------------------------------------------------------------
                try:
                    lugar_sucio = oferta_d.find_all("span",class_="PageProjectViewLogout-detail-reputation-item-locationItem")
                    oferta["lugar"] = lugar_sucio[1].text.strip()
                     
                except: 
                    oferta["lugar"] = "NO DEFINIDO"
                
                #print("lugar_oferta: "+oferta["lugar"] )

                #------------------------------------------------------------------------
                try: 
                    oferta["id_anuncioempleo"] = oferta_d.find_all("p",class_="PageProjectViewLogout-detail-tags")
                    ofertaAux = oferta["id_anuncioempleo"]
                    for oferta2 in ofertaAux:
                        
                        coincidencia2=str(oferta2).count("proyecto")
                        if coincidencia2 == 1:
                            oferta3=oferta2.text.strip()
                            oferta3=oferta3[18:]
                            oferta["id_anuncioempleo"] = oferta3
                           
                except: 
                    oferta["id_anuncioempleo"] = "No detallado"
                


                #print("id_anuncioempleo: "+ oferta["id_anuncioempleo"])
                
                
                #------------------------------------------------------------------------
                #EL ID DEL ANUNCIO NO DEBE REPETIRSE
                redundancia2 = controller.evitar_redundancia_por_id_anuncio(con, oferta)
                
                if(redundancia2 is not None):
                    print("ID ANUNCIO REPETIDO")
                    continue 
                #------------------------------------------------------------------------

                detalle_oferta = ""
                try: 
                    descripcion_oferta = oferta_d.find_all("p",class_="")

                    for ofertax in descripcion_oferta:
                        
                        oferta_limpia = str(ofertax.text.strip())
                        detalle_oferta = detalle_oferta + oferta_limpia

                    oferta["detalle"]= detalle_oferta[:2000]

                except:
                    oferta["detalle"] = "No detallado"
                
                #print(oferta["detalle"])

                #------------------------------------------------------------------------

                
                #------------------------------------------------------------------------
                #------------------------------------------------------------------------

                lista_oferta.append(oferta)  
                row_id = controller.registrar_oferta(con, oferta)
                print("ROW_ID")
                print(row_id)
                #print("ROW_ID")
                scraping_ofertadetalle(link, row_id, con)

                print("--------------------------------------------------------------------------------------")
            else:
                print("Registro redundante")

    return lista_oferta


def scraping_ofertadetalle(url_pagina, row_id, con):
    
    controller = Controller()
    detalle = {}
    detalle["id_oferta"] = row_id
    #print(detalle["id_oferta"])
    req = requests.get(url_pagina)
    soup = BeautifulSoup(req.text, "lxml")
    
    #OFERTA DETALLE
    try: 
        descripcion_oferta = soup.find_all("p",class_="")

        for oferta in descripcion_oferta:
                            
            oferta_limpia = str(oferta.text.strip())  
            detalle["descripcion"]= oferta_limpia
            print("DETALLE_OFERTA_DETALLE:"+detalle["descripcion"])
            if(detalle["descripcion"] == " " or detalle["descripcion"] == "" or len(detalle["descripcion"])==0):
                print("VACIO")
            else:
                controller.registrar_oferta_detalle(con, detalle)
            #controller.registrar_oferta_detalle(con, detalle)                                             
    except:
        detalle["descripcion"] = "No detallado"
        controller.registrar_oferta_detalle(con, detalle)
    print("--------------------------------------------------------------------------------------")
    return 1


def replace_quote(list):
    new_list = []
    for el in list:
        el = el.replace("'", "''")
        new_list.append(el)
    return new_list


def obtener_lista_keywords(con):
    controller = Controller()
    lista_busquedas = []
    i = 1
    for search in controller.obtener_keyword_search(con): 
        busqueda = {}
        if search != None:
            busqueda["descripcion"] = '/?keyword=' + search[0].replace(" ", " ").replace(".", "")
            busqueda["id"] = i
            lista_busquedas.append(busqueda)
            i += 1

    return lista_busquedas


def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',cadena) if unicodedata.category(c) != 'Mn'))
    return s.upper()

def fecha_publicacion(modalidad, tiempo):
    if(tiempo == "UN"):
        tiempo = 1

    tiempo = int(tiempo)
    switcher = {
        "HORAS": datetime.now() + timedelta(days=-tiempo/24),       
        "DIA":   datetime.now() + timedelta(days=-1),
        "DIAS":  datetime.now() + timedelta(days=-tiempo),
        "MES":   datetime.now() + timedelta(days=-30),
        "MESES": datetime.now() + timedelta(days=-tiempo*30)
    }
    return switcher.get(modalidad,datetime.now())