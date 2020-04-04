from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests

from dinos import data


options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/brave"
chrome_driver_binary = "/usr/bin/chromedriver"
driver = webdriver.Chrome(chrome_driver_binary, options=options)

url = "https://en.wikipedia.org/wiki/"
api = "http://localhost:5000/dino/create"

for d in data:
    driver.get(url + d)
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    main = soup.find('div', {'class':'mw-parser-output'})

    table = main.find('table', {'class':'infobox biota'})
    tr = table.find('tbody').findAll('tr', recursive=False)

    for elem in tr:
        try: print (elem.findAll('td')[1].find('a'))
        except IndexError: pass


    img = main.findAll('img')

    image = img[0]['src']

    text = ''
    for elem in main.findAll(['h2', 'h3', 'p', 'ul'], recursive=False):
        if elem.text == "References[edit]":
            break

        if elem.name == "p":
            text += elem.text
        elif elem.name in ["h2", "h3", "ul"]:
            text += elem.text + '\n'

    
    data = {"name": d, "content": text, "parent":"", "img":image}
    ''' print (requests.post(api, data).text) '''
