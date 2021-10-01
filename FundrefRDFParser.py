import rdflib
import pickle
import argparse
import json
import csv
from rdflib import URIRef
from rdflib.namespace import RDF, SKOS

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

def get_funder_labels(funder):
    labels = []
    if "skos-xl_prefLabel" in funder:
        labels.append(funder["skos-xl_prefLabel"])
    if "skos-xl_altLabel" in funder:
        labels.extend(funder["skos-xl_altLabel"].split("||"))
    return labels

def rdf_to_graph_pickle():
    g = rdflib.Graph()
    result = g.parse("registry.rdf")
    
    with open("registry.pickle", "wb") as f:
        pickle.dump(g, f, pickle.HIGHEST_PROTOCOL)

def graph_pickle_to_full_metadata_csv(canada_processing):
    try:
        with open("registry.pickle", "rb") as f:
            print("Loading registry.pickle...")
            g = pickle.load(f)
    except FileNotFoundError as e:
        print("registry.pickle not found; run with --graphpickle first")
        exit()

    # Get DOIs
    funderDOIs = list(g.subjects(RDF.type, SKOS.Concept))

    # Labels for CSV header
    uris_to_labels = {
        "doi": "doi",
        "excluded": "excluded",
        "http://www.w3.org/2008/05/skos-xl#prefLabel": "skos-xl_prefLabel",
        "prefLabel_lang": "prefLabel_lang",
        "http://www.w3.org/2008/05/skos-xl#altLabel": "skos-xl_altLabel",
        "previousLabel": "previousLabel",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/country": "crossref_country",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/state": "crossref_state",
        "http://purl.org/dc/terms/created": "dcterms_created",
        "http://purl.org/dc/terms/modified": "dcterms_modified",
        "primaryName_en": "primaryName_en",
        "primaryName_fr": "primaryName_fr",
        "primaryName_other": "primaryName_other",
        "nonDisplayNames": "nonDisplayNames",
        "altNames_en": "altNames_en",
        "altNames_fr": "altNames_fr",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/fundingBodyType": "crossref_fundingBodyType",
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
        "https://none.schema.org/address": "schema.org_address",
        "http://data.crossref.org/fundingdata/xml/schema/grant/grant-1.2/taxId": "crossref_taxId",
        "http://www.w3.org/2004/02/skos/core#inScheme": "skos-core_inScheme",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "rdf-syntax-ns_type",
        "ror_preferred": "ror_preferred",
        "ror_secondary": "ror_secondary"
    }

    output_filename = "funder_metadata.csv"
    if canada_processing:
        output_filename = "funder_metadata_canada.csv"
        # set up ROR lookup
        print("Preparing mapping from Crossref Funder Registry to ROR..")
        fundref_to_ror = map_fund_ref_to_ror()

        canada_geonames = {
            "http://sws.geonames.org/6141242/": "Saskatchewan",
            "http://sws.geonames.org/6093943/": "Ontario",
            "http://sws.geonames.org/6115047/": "Quebec",
            "http://sws.geonames.org/5909050/": "British Columbia",
            "http://sws.geonames.org/5883102/": "Alberta",
            "http://sws.geonames.org/6065171/": "Manitoba",
            "http://sws.geonames.org/6087430/": "New Brunswick",
            "http://sws.geonames.org/6091530/": "Nova Scotia",
            "http://sws.geonames.org/6354959/": "Newfoundland and Labrador",
            "http://sws.geonames.org/6113358/": "Prince Edward Island",
            "http://sws.geonames.org/6091069/": "Northwest Territories",
            "http://sws.geonames.org/6091732/": "Nunavut"
        }
    else:
        # remove columns not used
        for column in ["primaryName_en", "primaryName_fr", "primaryName_other", "nonDisplayNames", "altNames_en", "altNames_fr", "ror_preferred", "ror_secondary"]:
            uris_to_labels.pop(column)

    # Get funder metadata
    allkeys = ["doi"]
    funderMetadata = {}

    print("Processing metadata for {} funders...".format(len(funderDOIs)))
    for funderDOI in funderDOIs:
        if len(funderMetadata) % 5000 == 0 and len(funderMetadata) > 0:
            print("Processed metadata for {} of {} funders".format(len(funderMetadata), len(funderDOIs)))
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
        if canada_processing and funderMetadata[funderDOI]['crossref_country'] == "http://sws.geonames.org/6251999/":
            # Add human-readable name for Canada
            funderMetadata[funderDOI]['crossref_country'] = "Canada"
            # Replace states geonames URIs with provinces
            if "crossref_state" in funderMetadata[funderDOI] and funderMetadata[funderDOI]["crossref_state"] in canada_geonames:
                funderMetadata[funderDOI]["crossref_state"] = canada_geonames[funderMetadata[funderDOI]["crossref_state"]]

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
                if termsusageFlag and "acronym" in termsusageFlag: # acronyms
                    nonDisplay.append(str(altLabelLiteral))
                elif altLabelLiteral.language == "en": # English, not acronyms
                    altLabels_en.append(str(altLabelLiteral))
                elif altLabelLiteral.language == "fr": # French, not acronyms
                    altLabels_fr.append(str(altLabelLiteral))
                else: # other languages, not acronyms
                    nonDisplay.append(str(altLabelLiteral))
            if len(nonDisplay) > 0:
                funderMetadata[funderDOI]["nonDisplayNames"] = "||".join(nonDisplay)
            if len(altLabels_en) > 0:
                funderMetadata[funderDOI]["altNames_en"] = "||".join(altLabels_en)
            if len(altLabels_fr) > 0:
                funderMetadata[funderDOI]["altNames_fr"] = "||".join(altLabels_fr)

    print("Processed metadata for {} of {} funders".format(len(funderMetadata), len(funderDOIs)))

    # Supplement with previous labels
    print("Adding previous labels from related funders...")
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
    # Add "excluded" flag to subjects with deprecated status or above relationships
    for subject_funderDOI in funderMetadata:
        subject_funder = funderMetadata[subject_funderDOI]
        if "crossref_termsstatus" in subject_funder and "Deprecated" in subject_funder["crossref_termsstatus"]:
            funderMetadata[URIRef(subject_funderDOI)]["excluded"] = "excluded"
        for relation in ["crossref_incorporatedInto", "dcterms_isReplacedBy", "crossref_mergedWith", "crossref_renamedAs", "crossref_splitInto"]:
            if relation in subject_funder:
                funderMetadata[URIRef(subject_funderDOI)]["excluded"] = "excluded"
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

    print("Writing data to {}...".format(output_filename))
    # Write funder metadata to csv file
    with open(output_filename, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=list(uris_to_labels.values()))
        csvwriter.writeheader()
        for funderDOI in funderMetadata:
            csvwriter.writerow(funderMetadata[funderDOI])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--graphpickle', action='store_true', default=False)
    parser.add_argument('--metadatacsv', action='store_true', default=False)
    parser.add_argument('--canada', action='store_true', default=False)
    args = parser.parse_args()

    if args.graphpickle:
        print("Generating registry.pickle from registry.rdf...")
        rdf_to_graph_pickle()
    if args.metadatacsv:
        if args.canada:
            print("Generating funder_metadata_canada.csv from registry.pickle (with Canadian processing)...")
        else:
            print("Generating funder_metadata.csv from registry.pickle (no Canadian processing)...")
        graph_pickle_to_full_metadata_csv(args.canada)


if __name__ == "__main__":
    main()