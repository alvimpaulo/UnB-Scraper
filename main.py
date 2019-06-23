import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import json


class Course:
    def __init__(self, code="000000", departAcronym="SIGLA", name="NOME"):
        self.code = code
        self.departAcronym = departAcronym
        self.name = name


class Department:
    def __init__(self, course):
        self.course = course


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
                    flagNoPreriquisites = False

                    orgaoCurso = ""
                    codigoCurso = int(departOfferTds[0].get_text())
                    nomeCurso = departOfferTds[1].get_text()
                    nivelCurso = ""
                    incioVigenciaCurso = ""
                    preRequisitosDictArray = []
                    ementaCurso = ""
                    programaCurso = ""
                    bibliografiaCurso = ""

                    linkOfertaCurso = departOfferTds[1].a["href"]
                    linkEmentaCurso = departOfferTds[2].a["href"].replace(
                        "/graduacao/", "")

                    print(
                        f"Codigo da disciplina: {codigoCurso}\tNome da disciplina: {nomeCurso}")

                    siteEmentaCurso = requests.get(
                        f"https://matriculaweb.unb.br/graduacao/{linkEmentaCurso}")
                    ementaCursoSoup = BeautifulSoup(
                        siteEmentaCurso.content,  features="lxml")
                    tabelasEmentaCurso = ementaCursoSoup.find_all(
                        "table", {"id": "datatable"})

                    for tabelaEmentaCurso in tabelasEmentaCurso:
                        trsEmentaCurso = tabelaEmentaCurso.find_all("tr")

                        if(trsEmentaCurso.__len__() > 0):
                            flagPulaTr = False
                            for trIndice, trEmentaCurso in enumerate(trsEmentaCurso):
                                # if last row had a double th
                                if(flagPulaTr == True):
                                    flagPulaTr = False
                                    continue

                                thEmenta: str = trEmentaCurso.th.get_text()
                                tdEmenta: str = trEmentaCurso.td.prettify()

                                if(trEmentaCurso.th.get('rowspan') == '2'):
                                    flagPulaTr = True
                                    tdEmenta = tdEmenta + \
                                        trsEmentaCurso[trIndice+1].prettify()
                                if(thEmenta == "Pré-requisitos"):
                                    preRequisitos = re.split(
                                        r"<strong>\s+OU\s+<\/strong>", tdEmenta)

                                    for preRequisitostr in preRequisitos:
                                        if(flagNoPreriquisites):
                                            break
                                        preRequisitosDict = []

                                        PreRequisitosDict = re.split(
                                            r"<strong>\s+E\s+<\/strong>", preRequisitostr)

                                        for singlePreRequisitosHTML in PreRequisitosDict:
                                            singlepreRequisitosoup = BeautifulSoup(
                                                singlePreRequisitosHTML, features="lxml")
                                            singlePreRequisitos = singlepreRequisitosoup.get_text()
                                            singlePreRequisitos = singlePreRequisitos.strip()

                                            if(singlePreRequisitos == ""):
                                                print("pre-requisito vazio")
                                                break

                                            if(re.search(r"Disciplina sem pré-requisitos", singlePreRequisitos)):
                                                flagNoPreriquisites = True
                                                break

                                            singlePreRequisitosMatch = re.search(
                                                r"\s*([A-Z#]+)\s*(\d+)\s*(.+)\s*", singlePreRequisitos)

                                            preRequisitosDict.append({
                                                "departAcronym": singlePreRequisitosMatch.group(1),
                                                "codigoCurso": singlePreRequisitosMatch.group(2),
                                                "nomeCurso": singlePreRequisitosMatch.group(3)
                                            })
                                        preRequisitosDictArray.append(
                                            preRequisitosDict)
                                if(thEmenta == "Órgão"):
                                    orgaoCurso = BeautifulSoup(
                                        tdEmenta, features="lxml").getText().strip()
                                if(thEmenta == "Nível"):
                                    nivelCurso = BeautifulSoup(
                                        tdEmenta, features="lxml").getText().strip()
                                if(thEmenta == "Início da Vigência em"):
                                    incioVigenciaCurso = BeautifulSoup(
                                        tdEmenta, features="lxml").getText().strip()
                                if(thEmenta == "Ementa"):
                                    ementaCurso = BeautifulSoup(
                                        tdEmenta, features="lxml").getText().strip()
                                if(thEmenta == "Programa"):
                                    programaCurso = BeautifulSoup(
                                        tdEmenta, features="lxml").getText().strip()
                                if(thEmenta == "Bibliografia"):
                                    bibliografiaCurso = BeautifulSoup(
                                        tdEmenta, features="lxml").getText().strip()
                    coursesArray.append({
                        "codigo": codigoCurso,
                        "nome": nomeCurso,
                        "orgao": orgaoCurso,
                        "nivel": nivelCurso,
                        "inicioVigencia": incioVigenciaCurso,
                        "preRequisitos": preRequisitosDictArray,
                        "ementa": ementaCurso,
                        "programa": programaCurso,
                        "bibliografia": bibliografiaCurso
                    })
    sleep(1)

with open("./Courses-Information", "w", encoding='utf8') as file:
    file.write(json.dumps(coursesArray))
    pass
