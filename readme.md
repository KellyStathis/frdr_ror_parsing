# FRDR ROR Data Parsing

This project provides tools to parse ROR data into CSV files for FRDR.

## RORJsonParser.py
`RORJsonParser.py` parses the ROR data dump (JSON) to a CSV file for use in FRDR affiliation metadata. 

Optionally, it can process an override file which specifies a name in English, a name in French, and additional alternate names for specified ROR IDs. Overrides should be specified in TSV format with columns **id**, **name_en**, **name_fr**, and **altnames**.

All source files should be placed in the registry_data folder.

Usage: `python RORJsonParser.py --data ror-data.json --overrides ror_overrides.tsv`

The output file `frdr_affiliation_metadata.csv` has the following columns:

-  **id**: ROR ID
-  **country_code**: two-letter country code from ROR
-  **name_en**: main name in ROR or name_en from override file
-  **name_fr**: main name in ROR or name_fr from override file
-  **altnames**: all labels, aliases, and acronyms in ROR - plus all altnames specified in override file - delimited by "||"
-  **tags**: "Signup" if organization should appear in FRDR new user application form (inclues all Canadian organizations that are not type "Company")


## Workflow Documentation
- [ROR: Workflows for FRDR](https://docs.google.com/document/d/1-5n_A9Wo9OzVdQ6OYk0vIKF0khsY6iQu3REMBGWP5K4/edit#)








