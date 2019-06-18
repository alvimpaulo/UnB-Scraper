import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import json

site = requests.get(
    "https://matriculaweb.unb.br/graduacao/oferta_dep.aspx?cod=1")

mainSoup = BeautifulSoup(site.content, features="lxml")
table = mainSoup.find_all("table", {"id": "datatable"})
trs = table[0].find_all("tr")
coursesArray = []

for row in trs:
    tds = row.find_all("td")
    if(tds.__len__() > 0):
        departCode = int(tds[0].get_text())
        departAcronym = tds[1].get_text()
        departDenom = tds[2].get_text()
        departLink = tds[2].a["href"]
        print(
            f"Codigo: {departCode}\tSigla:{departAcronym}\tDenominacao: {departDenom}")

        departOfferSite = requests.get(
            f"https://matriculaweb.unb.br/graduacao/{departLink}")
        sleep(1)
        departOfferSoup = BeautifulSoup(
            departOfferSite.content, features="lxml")

        departOfferTable = departOfferSoup.find_all(
            "table", {"id": "datatable"})
        if(departOfferTable.__len__() > 0):
            departOfferTrs = departOfferTable[0].find_all("tr")

            for departOfferRow in departOfferTrs:
                departOfferTds = departOfferRow.find_all("td")

                if(departOfferTds.__len__() > 0):
                    preRequisitesDictArray = []  # TODO: rename
                    flagNoPreriquisites = False

                    courseCode = int(departOfferTds[0].get_text())
                    courseName = departOfferTds[1].get_text()
                    courseOfferDataLink = departOfferTds[1].a["href"]
                    courseSyllabusLink = departOfferTds[2].a["href"].replace(
                        "/graduacao/", "")

                    print(
                        f"Codigo da disciplina: {courseCode}\tNome da disciplina: {courseName}")

                    courseSyllabusSite = requests.get(
                        f"https://matriculaweb.unb.br/graduacao/{courseSyllabusLink}")
                    courseSyllabusSoup = BeautifulSoup(
                        courseSyllabusSite.content,  features="lxml")
                    courseSyllabusTables = courseSyllabusSoup.find_all(
                        "table", {"id": "datatable"})

                    for courseSyllabusTable in courseSyllabusTables:
                        courseSyllabusTrs = courseSyllabusTable.find_all("tr")

                        if(courseSyllabusTrs.__len__() > 0):
                            for courseSyllabusTr in courseSyllabusTrs:
                                try:
                                    syllabusTh: str = courseSyllabusTr.th.get_text()
                                except:
                                    syllabusTh: str = ""

                                try:
                                    syllabusTd: str = courseSyllabusTr.td.prettify()
                                except:
                                    syllabusTd: str = ""

                                if(syllabusTh == "Pré-requisitos"):
                                    preRequisites = re.split(
                                        r"<strong>\s+OU\s+<\/strong>", syllabusTd)

                                    for preRequisiteStr in preRequisites:
                                        if(flagNoPreriquisites):
                                            break
                                        preRequisitesDict = []

                                        preRequisiteDict = re.split(
                                            r"<strong>\s+E\s+<\/strong>", preRequisiteStr)

                                        for singlePreRequisiteHTML in preRequisiteDict:
                                            singlePreRequisiteSoup = BeautifulSoup(
                                                singlePreRequisiteHTML, features="lxml")
                                            singlePreRequisite = singlePreRequisiteSoup.get_text()
                                            singlePreRequisite = singlePreRequisite.strip()

                                            if(singlePreRequisite == ""):
                                                print("pre-requisito vazio")
                                                break

                                            if(re.search(r"Disciplina sem pré-requisitos", singlePreRequisite)):
                                                flagNoPreriquisites = True
                                                break

                                            singlePreRequisiteMatch = re.search(
                                                r"\s*([A-Z#]+)\s*(\d+)\s*(.+)\s*", singlePreRequisite)

                                            preRequisitesDict.append({
                                                "departAcronym": singlePreRequisiteMatch.group(1),
                                                "courseCode": singlePreRequisiteMatch.group(2),
                                                "courseName": singlePreRequisiteMatch.group(3)
                                            })
                                        preRequisitesDictArray.append(
                                            preRequisitesDict)

                    coursesArray.append({
                        "courseCode": courseCode,
                        "courseName": courseName,
                        "preRequisites": preRequisitesDictArray
                    })
    sleep(1)

with open("./Courses-Information", "w", encoding='utf8') as file:
    file.write(json.dumps(coursesArray))
    pass
