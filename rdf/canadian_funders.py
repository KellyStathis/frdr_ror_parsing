import rdflib
import pickle

with open('registry.pickle', 'rb') as f:
    g = pickle.load(f)

print(len(g))

## Build list of Canadian funders by DOI
canadianFunderDOIs = [] # doi
canadianFunderNameURLs = [] # doi, url
canadianFunderNames = [] # doi, name

# Get DOIs
for s,p,o in g:
    if "country" in p: #"http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/country"
        if "http://sws.geonames.org/6251999/" in o:
            canadianFunderDOIs.append(s)

# Get name label URLs
for doi in canadianFunderDOIs:
    for s,p,o in g.triples((doi, None, None)):
        if "http://www.w3.org/2008/05/skos-xl#prefLabel" in p:
            canadianFunderNameURLs.append([doi, o])

# Get names
for funder in canadianFunderNameURLs:
    doi = funder[0]
    url = funder[1]
    for s, p, o in g.triples((url, None, None)):
        if "http://www.w3.org/2008/05/skos-xl#literalForm" in p:
            canadianFunderNames.append([doi, o])

f = open ("canadianFunderNames.csv", "a")
for funder in canadianFunderNames:
    f.write(funder[0] + "," + "\"" + funder[1] + "\"" + "\n")
f.close()

