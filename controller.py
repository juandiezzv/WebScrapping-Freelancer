import preprocessing
from nltk import word_tokenize
from dboperation import DBWebscraping
from dboperation import DBOferta
from dboperation import DBOfertadetalle
from dboperation import DBKeyworSearch


class Controller:
    def __init__(self):
        self.dbwebscraping = DBWebscraping()
        self.dboferta = DBOferta()
        self.dbofertadetalle = DBOfertadetalle()
        self.dbkeywordsearch = DBKeyworSearch()

    def registrar_webscraping(self, con, webscraping):
        id = self.dbwebscraping.insert_webscraping(con, webscraping)
        return id

    def registrar_oferta(self, con, oferta):        
        idResult = self.dboferta.insert_oferta(con, oferta)            
        return idResult

    def registrar_ofertas(self, con, lista_oferta):
        print(len(lista_oferta))
        for oferta in lista_oferta:
            print("----------------analizando que hay en lista oferta---------------------")
            print(oferta)
            idPuesto = self.dboferta.insert_oferta(con, oferta)     

    def generar_insert_ofertadetalle(self, oferta):
        sql_insert = "INSERT INTO OFERTA_DETALLE (id_oferta,descripcion,fecha_creacion,fecha_modificacion) VALUES (%s,'%s',sysdate,sysdate);"
        sql_result = ""
        for ed in oferta["listaDescripcion"]:
            sql = sql_insert % (oferta["idPuesto"], ed)
            sql_result = sql_result + sql
        return sql_result

    def registrar_normalizado(self, con, lista):
        for element in lista:
            new_words = preprocessing.normalize_words(word_tokenize(element["descripcion"]))
            descripcion_normalizada = " ".join(new_words)
            element["descripcion_normalizada"] = descripcion_normalizada
        # DBOfertadetalle.update_requisito(con, element)

    def registrar_oferta_detalle(self, con, oferta_detalle):
        idResult = self.dbofertadetalle.insertOfertaDetalle(con, oferta_detalle)    

    def obtener_keyword_search(self, con):  
        return self.dbkeywordsearch.obtener_descripcion(con)

    def evitar_redundancia(self, con, oferta):
        return self.dboferta.evitar_redundancia(con, oferta)