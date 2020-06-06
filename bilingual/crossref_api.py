import json
import csv
import requests
import pickle

max_alt_names = 7 # Maximum present in Canadian funder data


funder_dois = []
funders = []

with open('canadianFunderNames.csv', 'r') as csv_file:
    readCSV = csv.reader(csv_file, delimiter=',')
    for row in readCSV:
        funder_dois.append(row[0])

count = 0
for doi in funder_dois:
    response = requests.get(doi)
    response_json = json.loads(response.content)
    prefLabel = response_json["prefLabel"]["Label"]["literalForm"]
    altLabels = []

    try:
        if isinstance(response_json["altLabel"], dict):
            altLabels = [response_json["altLabel"]["Label"]["literalForm"]]
        elif isinstance(response_json["altLabel"], list):
            for altLabel in response_json["altLabel"]:
                altLabels.append(altLabel["Label"]["literalForm"])
    except:
        altLabels = []

    funders.append({"doi": doi, "prefLabel": prefLabel, "altLabels": altLabels, "response_json": response_json})

    count = count+1
    if count % 10 == 0:
        print(count)

with open('canadian_funders.pickle', 'wb') as f:
    pickle.dump(funders, f, pickle.HIGHEST_PROTOCOL)

