import pickle
import csv

with open('funders.pickle', 'rb') as f:
    funders = pickle.load(f)

    def analyzeAltLabels(altLabels):
        altNames_en = []
        altNames_fr = []
        altAcronyms_en = []
        altAcronyms_fr = []
        for altLabel in altLabels:
            if altLabel["lang"] == "en":
                if altLabel["content"].isupper():
                    altAcronyms_en.append(altLabel)
                else:
                    altNames_en.append(altLabel)
            elif altLabel["lang"] == "fr":
                if altLabel["content"].isupper():
                    altAcronyms_fr.append(altLabel)
                else:
                    altNames_fr.append(altLabel)

        return altNames_en, altNames_fr, altAcronyms_en, altAcronyms_fr

    def altListToString(altList):
        altString = ""
        for altLabel in altList:
            altString = altString + "||" + altLabel["content"]

        return altString[2:]

    def processFunder(funder):
        altNames_en, altNames_fr, altAcronyms_en, altAcronyms_fr = analyzeAltLabels(funder["altLabels"])
        funder["prefLang"] = funder["prefLabel"]["lang"]
        funder["verification"] = False
        funder["label_en"] = ""
        funder["label_fr"] = ""
        funder["acronym_en"] = ""
        funder["acronym_fr"] = ""

        # Determine English and French labels and acronyms
        if funder["prefLang"] == "en":
            funder["label_en"] = funder["prefLabel"]["content"]  # en prefLabel --> label_en
            if len(altAcronyms_en) == 1:
                funder["acronym_en"] = altAcronyms_en[0]["content"]  # en alt acronym (1) --> acronym_en
            elif len(altAcronyms_en) > 1:
                funder["acronym_en"] = altListToString(altAcronyms_en)  # en alt acronym (>1) --> flag
                funder["verification"] = True
            if len(altNames_fr) == 1:
                funder["label_fr"] = altNames_fr[0]["content"]  # fr alt name (1) --> label_fr
                if len(altAcronyms_fr) == 1:
                    funder["acronym_fr"] = altAcronyms_fr[0]["content"]  # fr alt acronym (1) --> acronym_en
                elif len(altAcronyms_fr) > 1:
                    funder["acronym_fr"] = altListToString(altAcronyms_fr)  # fr alt acronym (>1) --> flag
                    funder["verification"] = True
            elif len(altNames_fr) > 1:
                funder["label_fr"] = altListToString(altNames_fr)  # fr alt name (>1) --> flag
                funder["verification"] = True
                funder["acronym_fr"] = altListToString(altAcronyms_fr)
        elif funder["prefLang"] == "fr":
            funder["label_fr"] = funder["prefLabel"]["content"]  # fr prefLabel --> label_fr
            if len(altAcronyms_fr) == 1:
                funder["acronym_fr"] = altAcronyms_fr[0]["content"]  # fr alt acronym (1) --> acronym_fr
            elif len(altAcronyms_fr) > 1:
                funder["acronym_fr"] = altListToString(altAcronyms_fr)  # fr alt acronym (>1) --> flag
                funder["verification"] = True
            if len(altNames_en) == 1:
                funder["label_en"] = altNames_en[0]["content"]  # en alt name (1) --> label_en
                if len(altAcronyms_en) == 1:
                    funder["acronym_en"] = altAcronyms_en[0]["content"]  # en alt acronym (1) --> acronym_en
                elif len(altAcronyms_en) > 1:
                    funder["acronym_en"] = altListToString(altAcronyms_en)  # en alt acronym (>1) --> flag
                    funder["verification"] = True
            elif len(altNames_en) > 1:
                funder["label_en"] = altListToString(altNames_en)  # en alt name (>1) --> flag
                funder["verification"] = True
                funder["acronym_en"] = altListToString(altAcronyms_en)

        # Get additional information from response_json
        funder["fundingBodyType"] = funder["response_json"]["fundingBodyType"]
        funder["fundingBodySubType"] = funder["response_json"]["fundingBodySubType"]

        funder["renamedAs"], funder["continuationOf"] = "", ""
        funder["replaces"], funder["isReplacedBy"] = "", ""
        funder["broader"], funder["narrower"] = "", ""

        if "renamedAs" in funder["response_json"]:
            funder["renamedAs"] = funder["response_json"]["renamedAs"]["resource"]
        if "continuationOf" in funder["response_json"]:
            funder["continuationOf"] = funder["response_json"]["continuationOf"]["resource"]
        if "replaces" in funder["response_json"]:
            funder["replaces"] = funder["response_json"]["replaces"]["resource"]
        if "isReplacedBy" in funder["response_json"]:
            funder["isReplacedBy"] = funder["response_json"]["isReplacedBy"]["resource"]

        if "broader" in funder["response_json"]:
            funder["broader"] = funder["response_json"]["broader"]["resource"]
        if "narrower" in funder["response_json"]:
            if isinstance(funder["response_json"]["narrower"], list):
                for narrower_funder in funder["response_json"]["narrower"]:
                    funder["narrower"] =  funder["narrower"] + "; " + (narrower_funder["resource"])
                funder["narrower"] =  funder["narrower"][2:]
            elif isinstance(funder["response_json"]["narrower"], dict):
                funder["narrower"] = funder["response_json"]["narrower"]["resource"]


        return funder

    def main():
        for funder in funders:
            funder = processFunder(funder)

        with open('canadianFundersBilingual.csv', 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header to CSV
            csvwriter.writerow(['doi', 'prefLang', "label_en", "acronym_en", "label_fr", "acronym_fr",
                                "fundingBodyType", "fundingBodySubType", "verification",
                                "renamedAs", "continuationOf", "replaces", "isReplacedBy",
                                "broader", "narrower"])

            # Write funders to CSV
            for funder in funders:
                csvwriter.writerow([funder['doi'], funder['prefLang'], funder["label_en"], funder["acronym_en"],
                                    funder["label_fr"], funder["acronym_fr"], funder["fundingBodyType"],
                                    funder["fundingBodySubType"], str(funder["verification"]),
                                    funder["renamedAs"], funder["continuationOf"],
                                    funder["replaces"], funder["isReplacedBy"],
                                    funder["broader"], funder["narrower"]])

    if __name__ == '__main__':
        main()
