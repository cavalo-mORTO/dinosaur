import requests

url = "https://www.google.com/search?q=Allosaurus"


print (requests.get(url).text)
