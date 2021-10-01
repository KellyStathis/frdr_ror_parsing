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
    parser.add_argument("--file", "-f", type=str, required=True)
    args = parser.parse_args()

    ror_data_list = load_json(args.file)

    # Write affiliation metadata to csv file
    column_names = ["id", "primary_name", "additional_names"]
    output_filename = "affiliation_metadata.csv"
    output_filepath = "output_data/" + output_filename

    print("Writing data to {}...".format(output_filename))

    with open(output_filepath, "w") as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=column_names)
        csvwriter.writeheader()
        for affiliation in ror_data_list:
            additional_names = affiliation["aliases"] + affiliation["acronyms"]
            for label in affiliation["labels"]:
                additional_names.append(label["label"])
            additional_names = "||".join(list(set(additional_names)))
            csvwriter.writerow({"id": affiliation["id"], "primary_name": affiliation["name"], "additional_names": additional_names})

if __name__ == "__main__":
    main()