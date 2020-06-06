## Canadian Crossref Funder Registry

This project exports all the Canadian entries in the Crossref Funder Registry in a CSV file. It also separates the labels and acronyms by language to support usage in bilingual applications.

## How to Use

### Requirements
This project requires Python 3 and the libraries json, csv, requets, rdflib, and pickle.

### Steps

1. Produce a list of all Canadian funders:
    - Download the latest version of the Crossref Funder Registry from here: [https://gitlab.com/crossref/open_funder_registry](https://gitlab.com/crossref/open_funder_registry)
    - Move this file into the `rdf` folder.
    - Run `rdf/registry_parse.py`. This will produce `registry.pickle`.
    - Run `rdf/canadian_funders.py`. This will produce `canadianFunderNames.csv` - a list of all Canadian Funder DOIs and the primary name associated.
2. Expand this list to include bilingual names and addtional metadata:
    -  Copy `canadianFunderNames.csv` to the `bilingual` directory.
    -  Run `bilingual/crossref_api.py` to produce `canadian_funders.pickle`.
    -  Run `bilingual/crossref_api_parse.py` to produce `canadianFundersBilingual.csv`.

Once you have `canadianFundersBilingual.csv`, there may be some additional cleanup required for entries that had *more than one possibility* for the English name, French name, English acronym, and/or French acronym. These entries have the value "TRUE" in the **verification** column.

The working copy of the results with clean metadata is here: [https://docs.google.com/spreadsheets/d/197dM9bN7LAPajk1Z0x3hg5axdMTJb-RP-FZrUc2j5AQ/edit#gid=786226888](https://docs.google.com/spreadsheets/d/197dM9bN7LAPajk1Z0x3hg5axdMTJb-RP-FZrUc2j5AQ/edit#gid=786226888)









