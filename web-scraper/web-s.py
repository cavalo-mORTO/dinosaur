from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re as regexp

from dinos import data


def main():
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/brave"
    chrome_driver_binary = "/usr/bin/chromedriver"
    driver = webdriver.Chrome(chrome_driver_binary, options=options)

    url = "https://en.wikipedia.org/wiki/"
    api = "http://localhost:5000/dino"

    for d in data:
        driver.get(url + d)
        content = driver.page_source
        soup = BeautifulSoup(content, features="lxml")
        content = soup.find('div', {'class':'mw-parser-output'})

        tree = family_tree(content)
        if tree is None:
            continue

        for i, item in enumerate(tree):
            if item == 'Animalia':
                tree[i] = 'Animal'
            elif item == 'Chordata':
                tree[i] = 'Chordate'
            elif item == 'Dinosauria':
                tree[i] = 'Dinosaur'
            elif item == 'Reptilia':
                tree[i] = 'Reptile'

        for i, branch in enumerate(tree):
            re = requests.get(api, params={"name":branch})
            print('Got ' + branch + ' with code '  +  str(re.status_code))
            if re.status_code == 404:
                parent = tree[i - 1]
                print(create_branch(driver, branch, parent))



def family_tree(content):
    parents = []

    try:
        table = content.find('table', {'class':'infobox biota'})
    except AttributeError:
        return None

    try:
        tr = table.find('tbody').findAll('tr', recursive=False)
    except AttributeError:
        return None

    for elem in tr:
        try: parents.append(elem.findAll('td')[1].find('a').text)
        except (IndexError, AttributeError): pass

    return parents

def create_branch(driver, name, parent=''):
    url = "https://en.wikipedia.org/wiki/"
    api = "http://localhost:5000/dino"

    req = requests.get(url + name)
    if req.status_code != 200:
        return 'Dinosaur not found! status code: ' + str(req.status_code)


    driver.get(url + name)
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    content = soup.find('div', {'class':'mw-parser-output'})
    
    name = soup.find('h1', {'class':'firstHeading'}).text
    images = content.findAll('img')
    image = images[0]['src']


    list_of_texts = []
    text = ''

    for elem in content.findAll(['h2', 'h3', 'p', 'ul'], recursive=False):
        
        if elem.name in ["p", "ul"]:
            new_text = regexp.sub(r'\[.{0,15}\]', '', elem.text)
            text += new_text
        elif elem.name in ["h2", "h3"]:
            try:
                title = elem.find_previous_sibling(['h2', 'h3']).text
                title = title.replace('[edit]', '')
            except AttributeError:
                title = None

            list_of_texts.append({'title': title, 'text': text})
            text = ''

        
        if elem.text in ["References[edit]", "References", "See also[edit]", "See also", "Notes[edit]", "Notes"]:
            break


    soup.decompose()
    data = {"name":name, "content":list_of_texts, "parent":parent, "img":image}
    post = requests.post(api + '/create', json=data)

    return 'Sent ' + data['name'] + ' with status code ' + str(post.status_code)


if __name__ == '__main__':
    main()
