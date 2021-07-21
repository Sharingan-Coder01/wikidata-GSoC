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

# Function to extract values for teachers and students
def extract(g, id):
    values = {}
    typeD = ""
    
    # ID's Teachers
    for _, _, teID in g.triples((BDR[id], BDO.personStudentOf, None)): 
        # Gets teachers of a person
        typeD = "teachers"
        _, _, teachID = NSM.compute_qname_strict(teID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(teachID)
    
    # ID's Students
    for _, _, stID in g.triples((BDR[id], BDO.personTeacherOf, None)):
        # Gets students of a person
        typeD = "students"
        _, _, studID = NSM.compute_qname_strict(stID)
        if typeD not in values:
            values[typeD] = []
        values[typeD].append(studID)
    
    return values

# Creates list with the extracted data
def createList(personID, vals, COUNTPROP):
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
    
    return row

# Wrapper function for all function call
def run(file_path, id, entity_list):
    ext_val = {}

    g = rdflib.ConjunctiveGraph()
    g.parse(file_path, format="trig")

    ext_val = extract(g, id)

    # Dictionary for number of teachers and students 
    COUNTPROP = {
        "teachers" : 40, 
        "students" : 80
    }

    nlist = createList(id, ext_val, COUNTPROP)
    entity_list.append(nlist)


# Function to create CSV using master list
def createCSV(all_list):
    with open('ExtractProp1.csv', "a") as f:
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

            if id.find("P0RK") == -1:
                run(file, id, main_list)
            else:
                continue
        
    createCSV(main_list)
    

if __name__ == "__main__":
    main()