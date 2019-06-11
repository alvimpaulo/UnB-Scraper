import requests
from bs4 import BeautifulSoup

site = requests.get(
    "https://matriculaweb.unb.br/graduacao/oferta_dep.aspx?cod=1")
content = site.content

mainSoup = BeautifulSoup(content)
table = mainSoup.find_all("table", {"id": "datatable"})
trs = table[0].find_all("tr")
for row in trs:
    tds = row.find_all("td")
    if(tds.__len__() > 0):
        print(
            f"Codigo: {tds[0].get_text()}\tSigla:{tds[1].get_text()}\tDenominacao: {tds[2].get_text()}")
