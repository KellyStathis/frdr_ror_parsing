import rdflib
import pickle
import argparse
import json
import csv
import requests
from rdflib import URIRef
from rdflib.namespace import RDF, SKOS

# Helper functions for metadata_pickle_to_metadata_csv
def map_fund_ref_to_ror():
    try:
        with open("ror-data.json", "r") as f:
            ror_data_list = json.load(f)
    except FileNotFoundError as e:
        print("ror-data.json not found")

    fundref_to_ror = {}
    for ror_entry in ror_data_list:
        if ror_entry["country"]["country_code"] == "CA":
            if "external_ids" in ror_entry and "FundRef" in ror_entry["external_ids"]:
                preferred_fundref_id = None
                all_fundref_ids = []

                # Get preferred and secondary FundRef IDs
                if "all" in ror_entry["external_ids"]["FundRef"]:
                    all_fundref_ids = ror_entry["external_ids"]["FundRef"]["all"]
                    if len(all_fundref_ids) == 1 and "preferred" in ror_entry["external_ids"]["FundRef"] and not \
                    ror_entry["external_ids"]["FundRef"]["preferred"]:
                        preferred_fundref_id = ror_entry["external_ids"]["FundRef"]["all"][0]
                if "preferred" in ror_entry["external_ids"]["FundRef"] and ror_entry["external_ids"]["FundRef"][
                    "preferred"]:
                    preferred_fundref_id = ror_entry["external_ids"]["FundRef"]["preferred"]
                if preferred_fundref_id in all_fundref_ids:
                    all_fundref_ids.remove(preferred_fundref_id)

                # Store preferred FundRef ID
                if preferred_fundref_id:
                    if preferred_fundref_id not in fundref_to_ror.keys():
                        fundref_to_ror[preferred_fundref_id] = {"preferred": [ror_entry["id"]]}
                    else:
                        if "preferred" in fundref_to_ror[preferred_fundref_id]:
                            fundref_to_ror[preferred_fundref_id]["preferred"] = fundref_to_ror[preferred_fundref_id][
                                "preferred"].append(preferred_fundref_id)
                        else:
                            fundref_to_ror[preferred_fundref_id] = {"preferred": ror_entry["id"]}

                # Store secondary FundRef IDs
                for secondary_fundref_id in all_fundref_ids:
                    if secondary_fundref_id not in fundref_to_ror.keys():
                        fundref_to_ror[secondary_fundref_id] = {"secondary": [ror_entry["id"]]}
                    else:
                        if "secondary" in fundref_to_ror[secondary_fundref_id]:
                            fundref_to_ror[secondary_fundref_id]["secondary"] = fundref_to_ror[secondary_fundref_id][
                                "secondary"].append(secondary_fundref_id)
                        else:
                            fundref_to_ror[secondary_fundref_id] = {"secondary": [ror_entry["id"]]}

    return fundref_to_ror

def process_funder_metadata(funder):
    funder_metadata = {}

    # Process non-name metadata
    for key in funder["response_json"].keys():
        if key not in ["prefLabel", "altLabel"]:
            if isinstance(funder["response_json"][key], str):
                funder_metadata[key] = funder["response_json"][key]
            elif isinstance(funder["response_json"][key], int):
                funder_metadata[key] = str(funder["response_json"][key])
            elif isinstance(funder["response_json"][key], dict):
                if len(funder["response_json"][key].keys()) == 1 and "resource" in funder["response_json"][key]:
                    funder_metadata[key] = funder["response_json"][key]["resource"]
                elif key == "address":
                    funder_metadata[key] = funder["response_json"][key]["postalAddress"]["addressCountry"]
                else:
                    print("Error: {}: dict has other keys besides 'resource': {}".format(key, funder["response_json"][key]))
            elif isinstance(funder["response_json"][key], list):
                funder_metadata[key] = []
                for item in funder["response_json"][key]:
                    if isinstance(item, dict) and len(item.keys()) == 1 and "resource" in item:
                        funder_metadata[key].append(item["resource"])
                    else:
                        print("Error: {}: list: {}".format(key, funder["response_json"][key]))
                funder_metadata[key] = "||".join(funder_metadata[key])
            else:
                print("Error: {}" + key + ": other type: {}".format(key, funder["response_json"][key]))

    # Process prefLabel and altLabel
    funder_metadata["prefLang"] = funder["response_json"]["prefLabel"]["Label"]["literalForm"]["lang"]
    funder_metadata["prefLabel"] = funder["response_json"]["prefLabel"]["Label"]["literalForm"]["content"]
    if funder_metadata["prefLang"] == "en":
        funder_metadata["primaryName_en"] = funder["response_json"]["prefLabel"]["Label"]["literalForm"]["content"]
    elif funder_metadata["prefLang"] == "fr":
        funder_metadata["primaryName_fr"] = funder["response_json"]["prefLabel"]["Label"]["literalForm"]["content"]
    else:
        funder_metadata["primaryName_other"] = funder["response_json"]["prefLabel"]["Label"]["literalForm"]["content"]

    if "altLabel" in funder["response_json"]:
        funder_metadata["nonDisplay"] = []
        funder_metadata["altNames_en"] = []
        funder_metadata["altNames_fr"] = []
        if isinstance(funder["response_json"]["altLabel"], dict):
            funder["response_json"]["altLabel"] = [funder["response_json"]["altLabel"]]
        for altLabel in funder["response_json"]["altLabel"]:
            if "content" in altLabel["Label"]["literalForm"]:
                # Add acronyms to non-display names
                if altLabel["Label"]["literalForm"]["content"].isupper():
                    funder_metadata["nonDisplay"].append(altLabel["Label"]["literalForm"]["content"])
                # Gather non-acronym English alternate names
                elif altLabel["Label"]["literalForm"]["lang"] == "en":
                    funder_metadata["altNames_en"].append(altLabel["Label"]["literalForm"]["content"])
                # Gather non-acronym French alternate names
                elif altLabel["Label"]["literalForm"]["lang"] == "fr":
                    funder_metadata["altNames_fr"].append(altLabel["Label"]["literalForm"]["content"])
                # Add non-English labels to non-display names
                else:
                    funder_metadata["nonDisplay"].append(altLabel["Label"]["literalForm"]["content"])
        funder_metadata["nonDisplay"] = "||".join(funder_metadata["nonDisplay"])
        funder_metadata["altNames_en"] = "||".join(funder_metadata["altNames_en"])
        funder_metadata["altNames_fr"] = "||".join(funder_metadata["altNames_fr"])

    return funder_metadata

def rdf_to_graph_pickle():
    g = rdflib.Graph()
    result = g.parse("registry.rdf")

    with open("registry.pickle", "wb") as f:
        pickle.dump(g, f, pickle.HIGHEST_PROTOCOL)

def get_funder_labels(funder):
    labels = []
    if "skos-xl_prefLabel" in funder:
        labels.append(funder["skos-xl_prefLabel"])
    if "skos-xl_altLabel" in funder:
        labels.extend(funder["skos-xl_altLabel"].split("||"))
    return labels

def graph_pickle_to_full_metadata_csv():
    try:
        with open("registry.pickle", "rb") as f:
            g = pickle.load(f)
    except FileNotFoundError as e:
        print("registry.pickle not found; run with --full_graphpickle first")
        exit()

    # Get DOIs
    funderDOIs = list(g.subjects(RDF.type, SKOS.Concept))

    # Labels for CSV header
    uris_to_labels = {
        "doi": "doi",
        "http://www.w3.org/2008/05/skos-xl#prefLabel": "skos-xl_prefLabel",
        "prefLabel_lang": "prefLabel_lang",
        "http://www.w3.org/2008/05/skos-xl#altLabel": "skos-xl_altLabel",
        "previousLabel": "previousLabel",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/country": "crossref_country",
        "http://purl.org/dc/terms/created": "dcterms_created",
        "http://purl.org/dc/terms/modified": "dcterms_modified",
        "primaryName_en": "primaryName_en",
        "primaryName_fr": "primaryName_fr",
        "primaryName_other": "primaryName_other",
        "nonDisplayNames": "nonDisplayNames",
        "altNames_en": "altNames_en",
        "altNames_fr": "altNames_fr",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/fundingBodyType": "crossref_fundingBodyType",
        "https://none.schema.org/address": "schema.org_address",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/fundingBodySubType": "crossref_fundingBodySubType",
        "http://data.crossref.org/fundingdata/termsstatus": "crossref_termsstatus",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/incorporatedInto": "crossref_incorporatedInto",
        "http://purl.org/dc/terms/isReplacedBy": "dcterms_isReplacedBy",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/mergedWith": "crossref_mergedWith",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/renamedAs": "crossref_renamedAs",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/splitInto": "crossref_splitInto",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/continuationOf": "crossref_continuationOf",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/incorporates": "crossref_incorporates",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/mergerOf": "crossref_mergerOf",
        "http://purl.org/dc/terms/replaces": "dcterms_replaces",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/splitFrom": "crossref_splitFrom",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/affilWith": "crossref_affilWith",
        "http://www.w3.org/2004/02/skos/core#broader": "skos-core_broader",
        "http://www.w3.org/2004/02/skos/core#narrower": "skos-core_narrower",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/region": "crossref_region",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/state": "crossref_state",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/taxId": "crossref_taxId",
        "http://www.w3.org/2004/02/skos/core#inScheme": "skos-core_inScheme",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "rdf-syntax-ns_type",
        "ror_preferred": "ror_preferred",
        "ror_secondary": "ror_secondary"
    }

    # Set up ROR lookup
    fundref_to_ror = map_fund_ref_to_ror()

    # Get funder metadata
    allkeys = ["doi"]
    funderMetadata = {}

    for funderDOI in funderDOIs:
        if len(funderMetadata) % 5000 == 0 and len(funderMetadata) > 0:
            print("Done {} of {} funders".format(len(funderMetadata), len(funderDOIs)))
        funderMetadata[funderDOI] = {"doi": str(funderDOI)}

        # Save metadata for all triples with funder as subject
        for p,o in g.predicate_objects(funderDOI):
            if p not in allkeys:
                allkeys.append(p)
            if "prefLabel" in p or "altLabel" in p:
                # Get string literal for label
                o = g.value(o, URIRef("http://www.w3.org/2008/05/skos-xl#literalForm"))
                if "prefLabel" in p:
                    funderMetadata[funderDOI]["prefLabel_lang"] = o.language
            if uris_to_labels[str(p)] not in funderMetadata[funderDOI]:
                funderMetadata[funderDOI][uris_to_labels[str(p)]] = str(o)
            else:
                funderMetadata[funderDOI][uris_to_labels[str(p)]] = funderMetadata[funderDOI][uris_to_labels[str(p)]] + "||" + str(o)

        # Enhance metadata for Canadian entries
        if funderMetadata[funderDOI]['crossref_country'] == "http://sws.geonames.org/6251999/":
            # Add related ROR IDs
            fundrefID = str(funderDOI).split("http://dx.doi.org/10.13039/")[1]
            if fundrefID in fundref_to_ror.keys():
                if "preferred" in fundref_to_ror[fundrefID]:
                    funderMetadata[funderDOI]["ror_preferred"] = "||".join(fundref_to_ror[fundrefID]["preferred"])
                if "secondary" in fundref_to_ror[fundrefID]:
                    funderMetadata[funderDOI]["ror_secondary"] = "||".join(fundref_to_ror[fundrefID]["secondary"])

            # Copy English and French prefLabels to separate columns
            if funderMetadata[funderDOI]["prefLabel_lang"] == "en":
                funderMetadata[funderDOI]["primaryName_en"] = funderMetadata[funderDOI]["skos-xl_prefLabel"]
            elif funderMetadata[funderDOI]["prefLabel_lang"] == "fr":
                funderMetadata[funderDOI]["primaryName_fr"] = funderMetadata[funderDOI]["skos-xl_prefLabel"]
            else:
                funderMetadata[funderDOI]["primaryName_other"] = funderMetadata[funderDOI]["skos-xl_prefLabel"]

            # Copy English and French altLabels to separate columns
            nonDisplay = []
            altLabels_en = []
            altLabels_fr = []
            for altLabel in g.objects(funderDOI, URIRef("http://www.w3.org/2008/05/skos-xl#altLabel")):
                altLabelLiteral = g.value(altLabel, URIRef("http://www.w3.org/2008/05/skos-xl#literalForm"))
                termsusageFlag = g.value(altLabel, URIRef("http://data.crossref.org/fundingdata/termsusageFlag"))
                if termsusageFlag and "acronym" in termsusageFlag:
                    nonDisplay.append(str(altLabelLiteral))
                elif altLabelLiteral.language == "en":
                    altLabels_en.append(str(altLabelLiteral))
                elif altLabelLiteral.language == "fr":
                    altLabels_fr.append(str(altLabelLiteral))
                else: # other languages, not acronyms
                    nonDisplay.append(str(altLabelLiteral))
            if len(nonDisplay) > 0:
                funderMetadata[funderDOI]["nonDisplayNames"] = "||".join(nonDisplay)
            if len(altLabels_en) > 0:
                funderMetadata[funderDOI]["altNames_en"] = "||".join(altLabels_en)
            if len(altLabels_fr) > 0:
                funderMetadata[funderDOI]["altNames_fr"] = "||".join(altLabels_fr)

    print("Done {} of {} funders".format(len(funderMetadata), len(funderDOIs)))

    # Supplement with previous labels
    # Add labels to subjects from the targets of: continuationOf, incorporates, mergerOf, replaces, and splitFrom
    for subject_funderDOI in funderMetadata:
        subject_funder = funderMetadata[subject_funderDOI]
        subject_previousLabels = []
        for relation in ["crossref_continuationOf", "crossref_incorporates", "crossref_mergerOf", "dcterms_replaces", "crossref_splitFrom"]:
            if relation in subject_funder:
                for target_funderDOI in subject_funder[relation].split("||"):
                    target_funder = funderMetadata[URIRef(target_funderDOI)]
                    subject_previousLabels.extend(get_funder_labels(target_funder))

        # Exclude labels that duplicate subject's current labels (prefLabel or altLabels)
        subject_currentLabels = get_funder_labels(subject_funder)
        subject_previousLabels = list(set(subject_previousLabels) - set(subject_currentLabels))

        if len(subject_previousLabels)  > 0:
            # Update subject's previousLabel in funderMetadata
            funderMetadata[subject_funderDOI]["previousLabel"] = "||".join(subject_previousLabels)

    # Add labels to targets from subjects with: incorporatedInto, isReplacedBy, mergedWith, renamedAs, and splitInto
    for subject_funderDOI in funderMetadata:
        subject_funder = funderMetadata[subject_funderDOI]
        for relation in ["crossref_incorporatedInto", "crossref_isReplacedBy", "crossref_mergedWith", "dcterms_renamedAs", "crossref_splitInto"]:
            if relation in subject_funder:
                for target_funderDOI in subject_funder[relation].split("||"):
                    target_funder = funderMetadata[URIRef(target_funderDOI)]
                    # Get labels from subject (to become previous labels for target)
                    subject_currentLabels = get_funder_labels(funderMetadata[subject_funderDOI])

                    # Exclude labels that duplicate target's current labels (prefLabel or altLabels)
                    target_currentLabels = get_funder_labels(target_funder)
                    subject_currentLabels = list(set(subject_currentLabels) - set(target_currentLabels))

                    if len(subject_currentLabels) > 0:
                        # Add subject's current labels as "previous labels" of target
                        if "previousLabel" not in target_funder:
                            # Update target's previousLabel in funderMetadata
                            funderMetadata[URIRef(target_funderDOI)]["previousLabel"] = "||".join(subject_currentLabels)
                        else:
                            target_previousLabels = target_funder["previousLabel"].split("||")
                            new_target_previousLabels = list(set(subject_currentLabels) - set(target_previousLabels))
                            if len(new_target_previousLabels) > 0:
                                # Update target's previousLabel in funderMetadata
                                target_previousLabels.extend(new_target_previousLabels)
                                funderMetadata[URIRef(target_funderDOI)]["previousLabel"] = "||".join(target_previousLabels)



    # Add any missing keys to uris_to_labels for csv header
    for key in allkeys:
        if str(key) not in uris_to_labels:
            uris_to_labels[str(key)] = str(key)

    with open("allFunderMetadata.csv", "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=list(uris_to_labels.values()))
        csvwriter.writeheader()
        for funderDOI in funderMetadata:
            csvwriter.writerow(funderMetadata[funderDOI])

    for col in allkeys:
        print(col)

def graph_pickle_to_can_list_csv():
    try:
        with open("registry.pickle", "rb") as f:
            g = pickle.load(f)
    except FileNotFoundError as e:
        print("registry.pickle not found; run with --full_graphpickle first")
        exit()

    print(len(g))

    # Build list of Canadian funders by DOI
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

def list_csv_to_can_metadata_pickle():
    funder_dois = []
    funders = []

    try:
        with open("canadianFunderNames.csv", "r") as csv_file:
            readCSV = csv.reader(csv_file, delimiter=",")
            for row in readCSV:
                doi = row[0]
                if doi not in funder_dois:
                    funder_dois.append(row[0])
    except FileNotFoundError as e:
        print("canadianFunderNames.csv not found; run with --can_listcsv first")
        exit()

    print("Processing {} funders...".format(len(funder_dois)))
    count = 0
    for doi in funder_dois:
        response = requests.get(doi)
        response_json = json.loads(response.content)
        funders.append({"doi": doi, "response_json": response_json})
        count = count + 1
        if count % 50 == 0:
            print("Done {} of {} funders".format(count, len(funder_dois)))
    print("Done {} of {} funders".format(count, len(funder_dois)))

    with open("canadian_funders.pickle", "wb") as f:
        pickle.dump(funders, f, pickle.HIGHEST_PROTOCOL)

def metadata_pickle_to_can_metadata_csv():
    try:
        with open("canadian_funders.pickle", "rb") as f:
            funders = pickle.load(f)
    except FileNotFoundError as e:
        print("canadian_funders.pickle not found; run with --can_metadatapickle first")
        exit()

    fundref_to_ror = map_fund_ref_to_ror()

    allkeys = ["id", "prefLabel", "prefLang", "primaryName_en", "primaryName_fr", "primaryName_other", "nonDisplay",
               "altNames_en", "altNames_fr", "fundingBodyType", "fundingBodySubType", "broader", "narrower",
               "incorporates", "splitFrom", "mergerOf", "replaces", "continuationOf", "renamedAs", "splitInto",
               "incorporatedInto", "mergedWith", "status", "affilWith", "taxId", "created", "modified", "country",
               "address", "state", "region", "inScheme"]
    processed_funders = []
    for funder in funders:
        funder_metadata = process_funder_metadata(funder)
        funder_metadata["doi"] = funder_metadata["id"]
        funder_metadata["id"] = funder["doi"].split("http://dx.doi.org/10.13039/")[1]
        if funder_metadata["id"] in fundref_to_ror.keys():
            if "preferred" in fundref_to_ror[funder_metadata["id"]]:
                funder_metadata["ror_id_preferred"] = "||".join(fundref_to_ror[funder_metadata["id"]]["preferred"])
            if "secondary" in fundref_to_ror[funder_metadata["id"]]:
                funder_metadata["ror_id_secondary"] = "||".join(fundref_to_ror[funder_metadata["id"]]["secondary"])
        processed_funders.append(funder_metadata)
        for key in funder_metadata.keys():
            if key not in allkeys:
                allkeys.append(key)
    print(allkeys)

    with open("canadianFunderMetadata.csv", "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=allkeys)
        csvwriter.writeheader()
        for funder in processed_funders:
            csvwriter.writerow(funder)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--full_graphpickle', action='store_true', default=False)
    parser.add_argument('--can_listcsv', action='store_true', default=False) # Canadian only
    parser.add_argument('--can_metadatapickle', action='store_true', default=False)
    parser.add_argument('--can_metadatacsv', action='store_true', default=False)
    parser.add_argument('--can_allsteps', action='store_true', default=False)
    parser.add_argument('--full_metadatacsv', action='store_true', default=False) # Export everything

    args = parser.parse_args()

    if args.full_graphpickle or args.can_allsteps:
        print("Generating registry.pickle from registry.rdf...")
        rdf_to_graph_pickle()
    if args.can_listcsv or args.can_allsteps:
        print("Generating canadianFunderNames.csv from registry.pickle...")
        graph_pickle_to_can_list_csv()
    if args.can_metadatapickle or args.can_allsteps:
        print("Generating canadian_funders.pickle from canadianFunderNames.csv...")
        list_csv_to_can_metadata_pickle()
    if args.can_metadatacsv or args.can_allsteps:
        print("Generating canadianFunderMetadata.csv from canadian_funders.pickle...")
        metadata_pickle_to_can_metadata_csv()
    if args.full_metadatacsv:
        print("Generating allFundersMetadata.csv from canadian_funders.pickle...")
        graph_pickle_to_full_metadata_csv()
    if not args.can_allsteps and not args.full_graphpickle and not args.can_listcsv and not args.can_metadatapickle and not args.can_metadatacsv and not args.full_metadatacsv:
        print("usage: must specify at least one of: --can_allsteps --full_graphpickle --can_listcsv --can_metadatapickle --can_metadatacsv --full_metadatacsv")

if __name__ == "__main__":
    main()