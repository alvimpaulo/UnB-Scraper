import requests
from bs4 import BeautifulSoup
from time import sleep

site = requests.get(
    "https://matriculaweb.unb.br/graduacao/oferta_dep.aspx?cod=1")
content = site.content

mainSoup = BeautifulSoup(content, features="lxml")
table = mainSoup.find_all("table", {"id": "datatable"})
trs = table[0].find_all("tr")
for row in trs:
    tds = row.find_all("td")
    if(tds.__len__() > 0):
        departCode = int(tds[0].get_text())
        departAcronym = tds[1].get_text()
        departDenom = tds[2].get_text()
        print(
            f"Codigo: {departCode}\tSigla:{departAcronym}\tDenominacao: {departDenom}")

        departOfferSite = requests.get(
            f"https://matriculaweb.unb.br/graduacao/oferta_dis.aspx?cod={departCode}")
        departOfferContent = departOfferSite.content
        departOfferSoup = BeautifulSoup(departOfferContent, features="lxml")

        departOfferTable = departOfferSoup.find_all(
            "table", {"id": "datatable"})
        if(departOfferTable.__len__() > 0):
            departOfferTrs = departOfferTable[0].find_all("tr")
            for departOfferRow in departOfferTrs:
                departOfferTds = departOfferRow.find_all("td")
                if(departOfferTds.__len__() > 0):
                    courseCode = int(departOfferTds[0].get_text())
                    courseName = departOfferTds[1].get_text()
                    print(
                        f"Codigo da disciplina: {courseCode}\tNome da disciplina: {courseName}")
    sleep(1)
