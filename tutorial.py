# Python code to illustrate parsing of XML files
import csv
import requests
import xml.etree.ElementTree as ET

def loadRSS(url):
    resp = requests.get(url)
    with open('topnewsfeed.xml', 'wb') as f:
        f.write(resp.content)


def pareXML(xmlfile):



loadRSS('http://www.hindustantimes.com/rss/topnews/rssfeed.xml')
