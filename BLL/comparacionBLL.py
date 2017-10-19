#!/usr/bin/env python
# encoding: utf-8
import sys, os
import datetime
parent_dir=os.getcwd()
path= os.path.dirname(parent_dir)
sys.path.append(path)

import pymongo
from DAO.conexionMongo import *
import calendar
from datetime import datetime


client = pymongo.MongoClient("mongodb://admin:admin@ds147072.mlab.com:47072/db_tweets")

try:
    db = client.get_default_database() # Accedemos a la BD donde tenemos las colecciones
    tweetsClasificados = db.TWCLASIFICADO
except:
    print "Error en DB"

import sys, os
import xml.dom.minidom
from xml.dom.minidom import parse

catColor = {
    "Turismo": "#BF1E2E",
    "Industria": "#EF4136",
    "Empleo": "#F25A29",
    "Seguridad": "#F8931F",
    "Hacienda": "#FCB042",
    "Salud": "#F9EE35",
    "Comercio": "#F9EE34",
    "Educación": "#D8DE24",
    "Vivienda": "#8DC641",
    "Ciencia y tecnología": "#272262",
    "Medio ambiente": "#2B3991",
    "Economía": "#29AAE3",
    "Transporte": "#01A79D",
    "Demografía": "#2BB673",
    "Deporte": "#016738",
    "Energía": "#009345",
    "Urbanismo e infraestructuras": "#3AB54B",
    "Sector público": "#672D93",
    "Legislación y justicia": "#92278F",
    "Cultura y ocio": "#9E1F64",
    "Sociedad y bienestar": "#DA1C5C",
    "Medio Rural": "#9B8578"
    }

def getLeyenda(anyo, mes):
    diccTW = getTweet(anyo, mes)

    dicDataset = getDataset(anyo, mes)

    categorias = catColor.keys()

    leyenda = []

    for categoria in categorias:
        dicCat = {}
        dicCat["Categoria"] = categoria

        if diccTW.has_key(categoria):
            dicCat["Tweets"] = str(round(diccTW[categoria],2)) + " %"
        else:
            dicCat["Tweets"] = "0 %"

        if dicDataset.has_key(categoria):
            dicCat["Datasets"] = str(round(dicDataset[categoria],2)) + " %"
        else:
            dicCat["Datasets"] = "0 %"

        leyenda.append(dicCat)

    return leyenda


def getComparacion(anyo, mes):
    diccTW = getTweet(anyo, mes)

    dicDataset = getDataset(anyo, mes)

    categorias = catColor.keys()

    x = []
    y = []
    color = []
    tupla = []

    for categoria in categorias:
        porcTw = diccTW.get(categoria, 0)
        porcDs = dicDataset.get(categoria, 0)

        dif = porcDs-porcTw

        tupla.append((dif,categoria))


    tupla.sort(key=lambda diferCat: diferCat[0], reverse=True)

    for element in tupla:
        categoria = element[1]
        dif = element[0]

        x.append(categoria)
        y.append(dif)
        color.append(catColor[categoria])

    return x, y, color


def getTweet(anyo, mes):
    anyoA = int(anyo)
    mesA = int(mes)

    diasMes = int( calendar.monthrange(anyoA, mesA)[1] )
    #Se cambia el formato de la fecha para que tome desde la
    #primera hora del dias hasta la ultima hora del último día
    ini = anyo + '-' + mes + '-01 00:00:00'
    ini=datetime.strptime(ini,"%Y-%m-%d %H:%M:%S")

    fin = anyo + '-' + mes + '-'+ str(diasMes) + ' 23:59:59'
    fin=datetime.strptime(fin,"%Y-%m-%d %H:%M:%S")

    tw = tweetsClasificados.find({
                                    'fechaTweet':{
                                        '$gte': ini,
                                        '$lt':  fin
                                    }
                                })

    diccTW = {}
    for tweet in tw:
        categoria = str(tweet['categoria'].encode('UTF-8'))
        #se realiza la suma de los tweets por categoría
        diccTW[categoria] = diccTW.get(categoria, 0) + 1

    totalTw = sum(diccTW.values())

    for categoria,valor in diccTW.items():
        if valor == 0:
            porcentaje = 0
        else:
            porcentajeTw = (valor/float(totalTw))*100

        diccTW[categoria]=porcentajeTw

    return diccTW

def getDataset(anyo, mes):
    dicNombres = {
        'ciencia tecnologia': "Ciencia y tecnología",
        'comercio': "Comercio",
        'cultura ocio': "Cultura y ocio",
        'demografia': "Demografía",
        'deporte': "Deporte",
        'economia': "Economía",
        'educacion': "Educación",
        'empleo': "Empleo",
        'energia': "Energía",
        'hacienda': "Hacienda",
        'industria': "Industria",
        'legislacion justicia': "Legislación y justicia",
        'medio ambiente': "Medio ambiente",
        'medio rural': "Medio Rural",
        'salud': "Salud",
        'sector publico': "Sector público",
        'seguridad': "Seguridad",
        'sociedad bienestar': "Sociedad y bienestar",
        'transporte': "Transporte",
        'turismo': "Turismo",
        'urbanismo infraestructuras': "Urbanismo e infraestructuras",
        'vivienda': "Vivienda"
        }

    filename = 'catalogo_' + anyo + '_' + mes + '.rdf'

    if os.path.isfile("../FILES/"+filename):
        DOMTree = xml.dom.minidom.parse('../FILES/'+filename)
        coleccion = DOMTree.documentElement
        datasets = coleccion.getElementsByTagName('dcat:dataset')

        diccDataset={}
        for dataset in datasets:
            temas = dataset.getElementsByTagName('dcat:theme')
            for tema in temas:
                url =  tema.getAttribute('rdf:resource')
                catBruto = (url.split('/'))[-1]
                categoria = catBruto.replace('-', ' ')
                diccDataset[categoria] = diccDataset.get(categoria, 0) + 1

        totalDataset = sum(diccDataset.values())

        for categoria,valor in diccDataset.items():
            if valor == 0:
                porcentaje = 0
            else:
                porcentajeDataset = (valor/float(totalDataset))*100

            diccDataset[dicNombres[categoria]]=porcentajeDataset

        return diccDataset

    else:
        print "Sin datos"