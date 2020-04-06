from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re as regexp

from dinos import data


options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/brave"
chrome_driver_binary = "/usr/bin/chromedriver"
driver = webdriver.Chrome(chrome_driver_binary, options=options)

url = "https://en.wikipedia.org/wiki/"
api = "http://localhost:5000/dino"

def family_tree(main):
    parents = []
    table = main.find('table', {'class':'infobox biota'})
    tr = table.find('tbody').findAll('tr', recursive=False)

    for elem in tr:
        try: parents.append(elem.findAll('td')[1].find('a').text)
        except (IndexError, AttributeError): pass

    return parents

def create_branch(driver, name, parent=''):
    url = "https://en.wikipedia.org/wiki/"
    api = "http://localhost:5000/dino"

    driver.get(url + name)
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    main = soup.find('div', {'class':'mw-parser-output'})
    
    name = soup.find('h1', {'class':'firstHeading'}).text
    images = main.findAll('img')
    image = images[0]['src']


    list_of_texts = []
    text = ''

    for elem in main.findAll(['h2', 'h3', 'p', 'ul'], recursive=False):
        if elem.text == "References[edit]":
            break


        if elem.name in ["p", "ul"]:
            new_text = regexp.sub(r'\[[0-9]*\]', '', elem.text)
            text += new_text
        elif elem.name in ["h2", "h3"]:
            try:
                title = elem.find_previous_sibling(['h2', 'h3']).text
                title = title.replace('[edit]', '')
            except AttributeError:
                title = None

            list_of_texts.append({'title': title, 'text': text})
            text = ''

    soup.decompose()
    
    data = {"name":name, "content":list_of_texts, "parent":parent, "img":image}
    
    return 'Sent ' + data['name'] + ' with status code ' + str(requests.post(api + '/create', json=data).status_code)



for d in data:
    driver.get(url + d)
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    main = soup.find('div', {'class':'mw-parser-output'})

    tree = family_tree(main)

    for i, branch in enumerate(tree):
        re = requests.get(api, params={"name":branch})
        print(branch + ' with code '  +  str(re.status_code))
        if re.status_code == 404:
            parent = tree[i - 1]
            print(create_branch(driver, branch, parent))


