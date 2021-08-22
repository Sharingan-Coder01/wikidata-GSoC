# Code to extract multiple roles associated with a person. The roles extracted were mapped with the labels extracted by extract_Roles_Desc.py 
# The CSV sheet created was later attached with every_person_data.csv 
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
TOL = Namespace("http://api.treasuryoflives.org/resource/")
TMP = Namespace("http://purl.bdrc.io/ontology/tmp/")

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
NSM.bind("tol", TOL)
NSM.bind("tmp", TMP)

if rdflib.__version__ == '4.2.2':
    x = rdflib.term._toPythonMapping.pop(rdflib.XSD['gYear'])

converter = pyewts.pyewts()
g = rdflib.ConjunctiveGraph()
file_path = 'CachePersonRoles.trig'
g.parse(file_path, format = "trig")

# Extract roles for persons
def extractRole(mylist):
    for bdrcId, _, _ in g.triples((None, TMP.hasRole, None)):
        nlist = [] # Stores roles in list 
        _, _, lname1 = NSM.compute_qname_strict(bdrcId)
        nlist.append(lname1)
        for _, _, RoleId in g.triples((bdrcId, TMP.hasRole, None)):
            _, _, lname2 = NSM.compute_qname_strict(RoleId)
            nlist.append(lname2)
        
        mylist.append(nlist) # Appends list for one person to master list

# Function to create CSV with master list
def createCSV(mylist):
	with open('Roles_read.csv', "w") as f:
		writer = csv.writer(f)
		for row in mylist:
			writer.writerow(row)

def main():
    mylist = []
    extractRole(mylist)
    createCSV(mylist)

if __name__ == "__main__":
    main()