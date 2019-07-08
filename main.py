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
                    creditosCurso = ""

                    linkOfertaCurso = departOfferTds[1].a["href"]
                    linkEmentaCurso = departOfferTds[2].a["href"].replace(
                        "/graduacao/", "")

                    print(
                        f"Codigo da disciplina: {codigoCurso}\tNome da disciplina: {nomeCurso}")

                    siteOfertaCurso = requests.get(
                        f"https://matriculaweb.unb.br/graduacao/{linkOfertaCurso}")
                    ofertaCursoSoup = BeautifulSoup(
                        siteOfertaCurso.content, features='lxml')
                    tabelasOfertaCurso = ofertaCursoSoup.findAll(
                        "table", {'id': 'datatable'})

                    for tabelaOfertaCurso in tabelasOfertaCurso:
                        camposThead = []

                        if(not tabelaOfertaCurso.thead):
                            # tabela cabeçalho
                            trsOfertaCurso = tabelaOfertaCurso.findAll(
                                "tr", recursive=False)

                            for trOfertaCurso in trsOfertaCurso:
                                thOferta: str = trOfertaCurso.th.get_text()
                                tdOferta: str = trOfertaCurso.td.getText()

                                # Creditos
                                if(thOferta.find("Créditos") >= 0):
                                    creditosCurso = tdOferta
                        else:
                            # tabelas de oferta
                            oferta = {
                                "turma": "",
                                "vagas": "",
                                "turno": "",
                                "horario-local": [],
                                "professor": "",
                                "obs": ""
                            }
                            for campo in tabelaOfertaCurso.thead.tr.findAll("th"):
                                camposThead.append(campo.getText().lower())

                            trsOfertaCurso = tabelaOfertaCurso.tbody.findAll(
                                "tr", recursive=False)

                            tdsOfertaCurso = tabelaOfertaCurso.tbody.tr.findAll(
                                "td", recursive=False)
                            for tdOfertaCursoIndex, tdOfertaCurso in enumerate(tdsOfertaCurso):

                                if(tdOfertaCursoIndex in [0, 2, 4, 5]):
                                    oferta[camposThead[tdOfertaCursoIndex]
                                           ] = tdOfertaCurso.getText()
                                    continue

                                if(tdOfertaCursoIndex == 1):
                                    oferta["vagas"] = {
                                        "total": tdOfertaCurso.findAll("td")[2].getText(),
                                        "ocupadas": tdOfertaCurso.findAll("td")[5].getText(),
                                        "restantes": tdOfertaCurso.findAll("td")[8].getText()}
                                    continue

                                if(tdOfertaCursoIndex == 3):
                                    for tdOfertaCursoTable in tdOfertaCurso.findAll("table"):
                                        tdOfertaCursoTableTds = tdOfertaCursoTable.findAll(
                                            "td")
                                        oferta["horario-local"].append({
                                            "dia": tdOfertaCursoTableTds[0].getText(),
                                            "inicio": tdOfertaCursoTableTds[1].getText(),
                                            "termino": tdOfertaCursoTableTds[2].getText(),
                                            "local": tdOfertaCursoTableTds[4].getText()
                                        })
                                        continue

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
                        "bibliografia": bibliografiaCurso,
                        "creditos": creditosCurso,
                        "oferta": oferta
                    })
    sleep(1)

with open("./Courses-Information.json", "w", encoding='utf8') as file:
    file.write(json.dumps(coursesArray))
    pass
