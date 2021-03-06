# First code written to test and learn RDFLib extracting the names of persons
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


def get_names(g, entity):
    labels = {}
    aliases = {}
    count_bo = 0
    count_zh = 0
    count_en = 0
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
                if(lang == "bo"):
                    count_bo = count_bo + 1
                if(lang == "zh"):
                    count_zh = count_zh + 1
                if(lang == "en"):
                    count_en = count_en + 1

    return labels, aliases, count_bo, count_zh, count_en


def print_csv(labels, aliases, NBCOLSALIASES, ID):
    # labels at the beginning
    headers = []
    row = []
    row.append(ID)
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
            return
        for i in range(nbcols):
            if i < len(aliases[lang]):
                row.append(aliases[lang][i])
            else:
                row.append("")

    with open('person_names.csv', 'a') as fd:
        writenow = csv.writer(fd)
        writenow.writerow(row)


def run(url_link, id):
    g = rdflib.ConjunctiveGraph()
    g.parse(url_link, format="turtle")
    labels, aliases, num_aliases_bo, num_aliases_zh, num_aliases_en = get_names(g, BDR[id])
    NBCOLSALIASES = {
        "bo": num_aliases_bo,
        "zh-hans": num_aliases_zh,
        "en": num_aliases_en
    }

    print_csv(labels, aliases, NBCOLSALIASES, id)


def main():
    l = os.listdir('persons/00')
    li = [x.split('.')[0] for x in l]

    link = 'http://purl.bdrc.io/graph/'

    person_links = []
    for i, f in enumerate(li):
        url_link = link + f
        person_links.append(url_link)

    for url in person_links:
        id = url.rsplit('/', 1)[-1]
        run(url, id)

if __name__ == "__main__":
    main()