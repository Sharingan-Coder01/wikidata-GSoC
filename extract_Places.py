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

# Function to get labels
def get_prefLabels(g, id):
    pplabels = {}
    for _, _, prefL in g.triples((BDR[id], SKOS.prefLabel, None)):
        prefLabelVal, lang = normalize(prefL)
        if lang not in pplabels:
            pplabels[lang] = []
        pplabels[lang].append(prefLabelVal)
    
    return pplabels

# function to get alternate labels
def get_altLabels(g, id):
    ppalias = {}
    for _, _, altL in g.triples((BDR[id], SKOS.altLabel, None)):
        altLabelVal, lang = normalize(altL)
        if lang not in ppalias:
            ppalias[lang] = []
        ppalias[lang].append(altLabelVal)
    
    return ppalias

# Function to extract values
def extractValues(g, id, f):
    PlaceType = ""
    Plabels = {}
    Paliases = {}
    lat = ""
    long = ""
    foundation = ""
    converted = ""
    tradStr = ""
    str1 = f

    if(str1 == "bdr:PT0037"):
        PlaceType = "monastery"
        
    elif(str1 == "bdr:PT0059"):
        PlaceType = "printery"

    elif(str1 == "bdr:PT0084"):
        PlaceType = "village"
    
    elif(str1 == "bdr:PT0050"):
        PlaceType = "nunnery"

    elif(str1 == "bdr:PT0028"):
        PlaceType = "lake"

    elif(str1 == "bdr:PT0008"):
        PlaceType = "city"

    elif(str1 == "bdr:PT0020"):
        PlaceType = "hamlet"
    
    elif(str1 == "bdr:PT0074"):
        PlaceType = "temple"

    Plabels = get_prefLabels(g, id)
    Paliases = get_altLabels(g, id)
    
    # Place Latitude
    for _, _, placeLat in g.triples((BDR[id], BDO.placeLat, None)):
        lat = placeLat
    
    # Place Longitude
    for _, _, placeLong in g.triples((BDR[id], BDO.placeLong, None)):
        long = placeLong
    
    # Date of Foundation
    for _, _, eveId in g.triples((BDR[id], BDO.placeEvent, None)):
        for _, _, event in g.triples((eveId, RDF.type, None)):
            _, _, check = NSM.compute_qname_strict(event)
            if(check == "PlaceFounded"):
                for _, _, date in g.triples((eveId, BDO.onYear, None)):
                    foundOn = date[:4]
                    foundation = foundOn

    # Date of Converion    
    for _, _, eveId in g.triples((BDR[id], BDO.placeEvent, None)):
        for _, _, event in g.triples((eveId, RDF.type, None)):
            _, _, check = NSM.compute_qname_strict(event)
            if(check == "PlaceConverted"):
                for _, _, date2 in g.triples((eveId, BDO.onYear, None)):
                    convertedOn = date2[:4]
                    converted = convertedOn

    # Associated Tradition
    for _, _, peveId in g.triples((BDR[id], BDO.placeEvent, None)):
        for _, _, extTrad in g.triples((peveId, BDO.associatedTradition, None)):
            _, _, tradName = NSM.compute_qname_strict(extTrad)
            tradStr = tradName[9:]


    return PlaceType, Plabels, Paliases, lat, long, foundation, converted, tradStr

# Function to store all data
def createList(LANGLABELS, BDRCid, PlaceType, Plabels, Paliases, lati, longi, foundationO, convertedO, AsTradition):
    row = []
    row.append(BDRCid)
    row.append(PlaceType)

    for lang in LANGLABELS.keys():
        if lang in Plabels and len(Plabels[lang]):
            if Plabels[lang][0] == "？" or Plabels[lang][0] == "？？":
                row.append("")
            else:
                row.append(Plabels[lang][0])
        else:
            row.append("")
    
    for lang in LANGLABELS.keys():
        if lang in Paliases and len(Paliases[lang]):
            if Paliases[lang][0] == "？" or Paliases[lang][0] == "？？":
                row.append("")
            else:
                row.append(Paliases[lang][0])
        else:
            row.append("")

    row.append(lati)
    row.append(longi)
    row.append(AsTradition)
    row.append(foundationO)
    row.append(convertedO)

    return row

# Function to create CSV 
def createCSV(all_list):
    with open('All_Places_Final.csv', "a") as f:
        writer = csv.writer(f)
        for r in all_list:
            writer.writerow(r)


def run(file_path, id, entity_list):
    Ptype = ""
    labels = {}
    aliases = {}
    latitude = ""
    longitude = ""
    foundationOnD = ""
    convertedOnD = ""
    AsscTrad = ""
    filter = ""

    g = rdflib.ConjunctiveGraph()
    g.parse(file_path, format="trig")

    for _, _, status in g.triples((BDA[id], ADM.status, None)):
        s = status.rsplit('/', 1)[-1]
        if s != "StatusReleased":
            return
    
    for _, _, placeID in g.triples((BDR[id], BDO.placeType, None)):
        nsshort, _, lname = NSM.compute_qname_strict(placeID)
        filter = nsshort + ':' + lname

    type_place_Do = ["bdr:PT0037", "bdr:PT0059", "bdr:PT0084" , "bdr:PT0050" , "bdr:PT0028" , "bdr:PT0008", "bdr:PT0020", "bdr:PT0074"]
    if filter in type_place_Do:
        Ptype, labels, aliases, latitude, longitude, foundationOnD, convertedOnD, AsscTrad = extractValues(g, id, filter)    
    else:
        return

    LANGLABELS = {
        "bo": 1,
        "zh-hans": 1,
        "en": 1,
        "zh-latn-pinyin-x-ndia" : 1,
        "mn-x-trans" : 1
    }

    plist = createList(LANGLABELS, id, Ptype, labels, aliases, latitude, longitude, foundationOnD, convertedOnD, AsscTrad)
    entity_list.append(plist)


def main():
    entity_list = []
    dir = os.listdir('places')
    folder = 'places/'
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
            run(file, id, entity_list)

    createCSV(entity_list)
    

if __name__ == "__main__":
    main()