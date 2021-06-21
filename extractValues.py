import rdflib
import os 
from rdflib.namespace import RDF, RDFS, SKOS, OWL, Namespace, NamespaceManager, XSD, URIRef
import csv
import pyewts
import sys

BDR = Namespace("http://purl.bdrc.io/resource/")
BDO = Namespace("http://purl.bdrc.io/ontology/core/")
BDA = Namespace("http://purl.bdrc.io/admindata/")
BDG = Namespace("http://purl.bdrc.io/graph/")
ADM = Namespace("http://purl.bdrc.io/ontology/admin/")
WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")
DILA = Namespace("http://purl.dila.edu.tw/resource/")
VIAF = Namespace("http://viaf.org/viaf/")

NSM = NamespaceManager(rdflib.Graph())
NSM.bind("bdr", BDR)
NSM.bind("bdg", BDG)
NSM.bind("bdo", BDO)
NSM.bind("bda", BDA)
NSM.bind("adm", ADM)
NSM.bind("skos", SKOS)
NSM.bind("rdfs", RDFS)
NSM.bind("wd", WD)
NSM.bind("owl", OWL)
NSM.bind("wdt", WDT)
NSM.bind("dila", DILA)
NSM.bind("viaf", VIAF)

# see https://github.com/RDFLib/rdflib/issues/806
if rdflib.__version__ == '4.2.2':
    x = rdflib.term._toPythonMapping.pop(rdflib.XSD['gYear'])

converter = pyewts.pyewts()

def normalize(literal):
    if literal.language == "bo-x-ewts":
        return [converter.toUnicode(literal.value), "bo"]
    return [literal.value, literal.language]


def extractVal(g, entity):
    labels = {}
    aliases = {}
    entity_gender = ""
    deathD = ""
    birthD = ""

    for _, _, prefL in g.triples((entity, SKOS.prefLabel, None)):
        prefLabelVal, lang = normalize(prefL)
        if lang not in labels:
            labels[lang] = []
        labels[lang].append(prefLabelVal)

    for _, _, nameR in g.triples((entity, BDO.personName, None)):
        for _, _, otherName in g.triples((nameR, RDFS.label, None)):
            otherNameVal, lang = normalize(otherName)
            if lang not in aliases:
                aliases[lang] = []
            if lang not in labels or otherNameVal not in labels[lang]:              
                aliases[lang].append(otherNameVal)

    for _, _, gender in g.triples((entity, BDO.personGender, None)):
        gen = gender.rsplit('/', 1)[-1]
        entity_gender = gen[6:]          

    for _,_, perEvent in g.triples((entity, BDO.personEvent, None)):
        for _, _, perE in g.triples((perEvent, RDF.type, None)):
            check_date = perE.rsplit('/', 1)[-1]
            if(check_date == "PersonDeath"):
                for _, _, date in g.triples((perEvent, BDO.onYear, None)):
                    deathD = date[:4]

            if(check_date == "PersonBirth"):
                for _, _, date in g.triples((perEvent, BDO.onYear, None)):
                    birthD = date[:4]         

    return labels, aliases, entity_gender, deathD, birthD


def createListVals(labels, aliases, NBCOLSALIASES, ID, gend, dateDeath, dateBirth, all_list):
    # labels at the beginning
    headers = []
    row = []
    row.append(ID)
    row.append(gend)
    row.append(dateBirth)
    row.append(dateDeath)
    # labels headers
    for lang in NBCOLSALIASES.keys():
        headers.append("label_%s" % lang)
    # aliases headers
    for lang, nbcols in NBCOLSALIASES.items():
        for i in range(nbcols):
            headers.append("alias_"+lang+"_"+str(i+1))
    # labels data
    for lang in NBCOLSALIASES.keys():
        if lang in labels and len(labels[lang]):
            row.append(labels[lang][0])
        else:
            row.append("")
    # aliases data
    for lang, nbcols in NBCOLSALIASES.items():
        if lang not in aliases:
            continue
        if nbcols < len(aliases[lang]):
            print("!!Error!! There should be at least %i columns for %s aliases" % (len(aliases[lang]), lang))
            print(ID)
            continue
        for i in range(nbcols):
            if i < len(aliases[lang]):
                row.append(aliases[lang][i])
            else:
                row.append("")
    
    all_list.append(row)


def createCSV(all_list):
    with open('every_person_data.csv', "a") as f:
        writer = csv.writer(f)
        for r in all_list:
            writer.writerow(r)

def run(file_path, id):
    g = rdflib.ConjunctiveGraph()
    g.parse(file_path, format="trig")
    entity_list = []
    for _, _, status in g.triples((BDA[id], ADM.status, None)):
        s = status.rsplit('/', 1)[-1]
        if s != "StatusReleased":
            return

    labels, aliases, gen, DD, BD = extractVal(g, BDR[id])

    NBCOLSALIASES = {
        "bo": 17,
        "zh-hans": 2,
        "en": 4
    }

    createListVals(labels, aliases, NBCOLSALIASES, id, gen, DD, BD, entity_list)
    createCSV(entity_list)


def main():
    dir = os.listdir('persons')
    folder = 'persons/'
    directories = []
    for dir_name in dir:
        if dir_name.find(".git") == -1:
            directory = folder + dir_name
            directories.append(directory)

        else:
            continue

    for d in directories:    
        l = os.listdir(d)

        person_links = []
        for f in l:
            file_p = d + "/" + f
            person_links.append(file_p)

        for file in person_links:
            c = file.rsplit('/', 1)[-1]
            id = c[:-5]

            if id.find("P0RK") == -1:
                run(file, id)
            
            else:
                continue


if __name__ == "__main__":
    main()