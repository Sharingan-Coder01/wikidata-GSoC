# Code to extract all kinship relations associated with a person
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


def extract(g, id):
    values = {}
    typeD = ""
    fatherID = ""
    motherID = ""
    wifeID = ""
    husbandID = ""

    # Relation hasSon
    for _, _, soID in g.triples((BDR[id], BDO.hasSon, None)):
        typeD = "son"
        _, _, sonID = NSM.compute_qname_strict(soID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(sonID)

    # Relation hasDaughter
    for _, _, daID in g.triples((BDR[id], BDO.hasDaughter, None)):
        typeD = "daughter"
        _, _, daugID = NSM.compute_qname_strict(daID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(daugID)

    # Relation hasBrother
    for _, _, broID in g.triples((BDR[id], BDO.hasBrother, None)):
        typeD = "brother"
        _, _, brotherID = NSM.compute_qname_strict(broID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(brotherID)

    # Relation hasYoungerBrother
    for _, _, ybroID in g.triples((BDR[id], BDO.hasYoungerBrother, None)):
        typeD = "Ybrother"
        _, _, ybrotherID = NSM.compute_qname_strict(ybroID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(ybrotherID)

    # Relation hasOlderBrother
    for _, _, ebroID in g.triples((BDR[id], BDO.hasOlderBrother, None)):
        typeD = "Ebrother"
        _, _, ebrotherID = NSM.compute_qname_strict(ebroID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(ebrotherID)

    # Relation hasSister
    for _, _, sisID in g.triples((BDR[id], BDO.hasSister, None)):
        typeD = "sister"
        _, _, sisterID = NSM.compute_qname_strict(sisID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(sisterID)

    # Relation hasElderSister
    for _, _, ysisID in g.triples((BDR[id], BDO.hasYoungerSister, None)):
        typeD = "Ysister"
        _, _, ysisterID = NSM.compute_qname_strict(ysisID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(ysisterID)

    # Relation hasYoungerSister
    for _, _, esisID in g.triples((BDR[id], BDO.hasOlderSister, None)):
        typeD = "Esister"
        _, _, esisterID = NSM.compute_qname_strict(esisID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(esisterID)

    # Relation hasFather
    for _, _, fID in g.triples((BDR[id], BDO.hasFather, None)):
        _, _, fathID = NSM.compute_qname_strict(fID)
        fatherID = fathID
    
    # Relation hasMother
    for _, _, mID in g.triples((BDR[id], BDO.hasMother, None)):
        _, _, mothID = NSM.compute_qname_strict(mID)
        motherID = mothID

    # Relation hasWife
    for _, _, wID in g.triples((BDR[id], BDO.hasWife, None)):
        _, _, wiID = NSM.compute_qname_strict(wID)
        wifeID = wiID

    # Relation hasHusband
    for _, _, hID in g.triples((BDR[id], BDO.hasHusband, None)):
        _, _, huID = NSM.compute_qname_strict(hID)
        husbandID = huID
    
    return values, fatherID, motherID, wifeID, husbandID

def createList(personID, vals, COUNTPROP, fValue, mValue, wValue, hValue):
    row = []
    row.append(personID)

    for tp, nbcols in COUNTPROP.items():
        if tp not in vals:
            continue
        if nbcols < len(vals[tp]):
            print("!!Error!! There should be at least %i columns for %s aliases" % (len(vals[tp]), tp))
            print(personID)
            continue
        for i in range(nbcols):
            if i < len(vals[tp]):
                row.append(vals[tp][i])
            else:
                row.append("")

    row.append(fValue)
    row.append(mValue)
    row.append(wValue)
    row.append(hValue)
    
    return row


def run(file_path, id, entity_list):
    ext_val = {}
    fatherV = ""
    motherV = ""
    wifeV = ""
    husbandV = ""
    
    g = rdflib.ConjunctiveGraph()
    g.parse(file_path, format="trig")

    ext_val = extract(g, id)

    COUNTPROP = {
        "son" : 6, 
        "daughter" : 6,
        "brother" : 4,
        "Ybrother" : 3,
        "Ebrother" : 3,
        "sister" : 2,
        "Ysister" : 1,
        "Esister" : 1
    }

    nlist = createList(id, ext_val, COUNTPROP, fatherV, motherV, wifeV, husbandV)
    entity_list.append(nlist)


# Function to create CSV 
def createCSV(all_list):
    with open('People_Relationship.csv', "a") as f:
        writer = csv.writer(f)
        for r in all_list:
            writer.writerow(r)


def main():
    main_list = []
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

            if id.find("P0RK") == -1:   #Filters BDRCID starting with P0RK
                run(file, id, main_list)
            else:
                continue
        
    createCSV(main_list)
    

if __name__ == "__main__":
    main()