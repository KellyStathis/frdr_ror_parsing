import argparse
import json
import csv

def load_json(filename):
    # Read affiliation metadata from ROR json data dump
    try:
        with open("registry_data/" + filename, "r") as f:
            print("Reading data from {}...".format(filename))
            ror_data_list = json.load(f)
            return ror_data_list
    except FileNotFoundError as e:
        print("{} not found: {}".format(filename, e))
    except json.JSONDecodeError as e:
        print("Could not process {} as JSON: {}".format(filename, e))
    except Exception as e:
        print(e)
    exit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", "-d", type=str, required=True)
    parser.add_argument("--overrides", "-o", type=str, required=False)
    args = parser.parse_args()

    # Load original ROR data
    ror_data_list = load_json(args.data)

    # Load overrides
    if args.overrides:
        ror_overrides = {}
        with open("registry_data/" + args.overrides, "r") as f:
            csvreader = csv.DictReader(f, delimiter="\t")
            for row in csvreader:
                ror_overrides[row["id"]] = {"name_en": row["name_en"], "name_fr": row["name_fr"], "altnames": row["altnames"]}

    # Write affiliation metadata to csv file
    column_names = ["id", "country_code", "name_en", "name_fr", "altnames"]
    output_filename = "affiliation_metadata_frdr.csv"
    output_filepath = "output_data/" + output_filename

    print("Writing data to {}...".format(output_filename))

    with open(output_filepath, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=column_names)
        csvwriter.writeheader()
        for affiliation in ror_data_list:
            name_en = affiliation["name"]
            name_fr = affiliation["name"]
            altnames = affiliation["aliases"] + affiliation["acronyms"]
            for label in affiliation["labels"]:
                altnames.append(label["label"])

            # Add overrides to ROR data
            if affiliation["id"] in ror_overrides:
                affiliation_override = ror_overrides[affiliation["id"]]

                # Override name_en and name_fr
                if affiliation_override["name_en"] or affiliation_override["name_fr"]:
                    name_en = affiliation_override["name_en"]
                    name_fr = affiliation_override["name_fr"]
                    # If there is no English name, use curated French name and vice versa
                    if not name_en:
                        name_en = name_fr
                    elif not name_fr:
                        name_fr = name_en
                    # Add original name to altnames, if needed
                    if affiliation["name"] != name_en and affiliation["name"] != name_fr:
                        altnames.append(affiliation["name"])

                # Add additional altnames from overrides
                if affiliation_override["altnames"]:
                    altnames += affiliation_override["altnames"].split("||")

            # Remove duplicates from altnames
            altnames = list(set(altnames))
            # Remove altnames that duplicate name_en or name_fr
            if name_en in altnames:
                altnames.remove(name_en)
            if name_fr in altnames:
                altnames.remove(name_fr)

            # Reformat altnames to "||"-delimited string
            altnames = "||".join(list(set(altnames)))

            csvwriter.writerow({"id": affiliation["id"], "country_code": affiliation["country"]["country_code"],
                                "name_en": name_en, "name_fr": name_fr, "altnames": altnames})

if __name__ == "__main__":
    main()