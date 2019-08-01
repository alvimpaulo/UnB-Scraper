import re
import pymongo
import urllib
import os

mongoUsername = os.environ["MONGODB_ATLAS_USERNAME"]
mongoPassword = os.environ["MONGODB_ATLAS_PASSWORD"]
client = pymongo.MongoClient(
    f"mongodb+srv://{mongoUsername}:{mongoPassword}@cluster0-ci3al.mongodb.net/test?retryWrites=true&w=majority")
db = client['unb-scrapper']
db.list_collection_names()
newData = db.get_collection('data-2019-02-pos-matricula')
regx = re.compile(r"Computação", re.IGNORECASE)
diasArray = [
    "Sexta", "Segunda", "Terça", "Quarta", "Quinta"
]
computacaoCourses = newData.find(
    {"orgao": regx, 'oferta': {'$elemMatch': {
        "vagas": {"$gt": "0"}
    }
    }
    })

for course in computacaoCourses:
    print(
        f"{course['nome']} https://matriculaweb.unb.br/graduacao/oferta_dados.aspx?cod={course['codigo']}&dep=116")

fileWriteInput = input("record in file? (Y/n): ")
if(fileWriteInput == "n"):
    pass

else:
    with open("./resultado-busca.txt", "w", encoding='utf8') as file:
        for course in computacaoCourses:
            file.write(
                f"{course['nome']} https://matriculaweb.unb.br/graduacao/oferta_dados.aspx?cod={course['codigo']}&dep=116\n")


""" regx = re.compile(r'jogo', re.IGNORECASE)
computacaoCourses = newData.find(
    {"programa": regx
     })
for course in computacaoCourses:
    print(
        f"{course['nome']} https://matriculaweb.unb.br/graduacao/oferta_dados.aspx?cod={course['codigo']}") """
