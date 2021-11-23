# FRDR Controlled Vocabularies

This project provides tools to parse ROR and Crossref Funder Registry data into CSV files for FRDR.

## Research Organization Registry (ROR)
`RORJsonParser.py` parses the ROR data dump (JSON) to a CSV file for use in FRDR affiliation metadata. 

Optionally, it can process an override file which specifies a name in English, a name in French, and additional alternate names for specified ROR IDs. Overrides should be specified in TSV format with columns **id**, **name_en**, **name_fr**, and **altnames**.

All source files should be placed in the registry_data folder.

Usage: `python RORJsonParser.py --data ror-data.json --override ror_overrides.tsv`

The output file `frdr_affiliation_metadata.csv` has the following columns:

-  **id**: ROR ID
-  **country_code**: two-letter country code from ROR
-  **name_en**: main name in ROR or name_en from override file
-  **name_fr**: main name in ROR or name_fr from override file
-  **altnames**: all labels, aliases, and acronyms in ROR - plus all altnames specified in override file - delimited by "||"


## Crossref Funder Registry
`FundrefRDFParser.py` parses the Crossref Funder Registry RDF file to a CSV file for use in FRDR funding metadata.

### Flags
Because the RDF graph takes a long time to process, execution can be separated into two steps with optional flags. If neither `--graphpickle` or `--metadatacsv` is specified, both steps will be executed.

Usage: `python FundrefRDFParser.py --graphpickle --metadatacsv`

- Step 1: `--graphpickle`: Generate registry.pickle from registry.rdf. (TODO: Allow users to specify this file name with --data parameter. File should be placed in registry_data.)
- Step 2: `--metadatacsv`: Generate funder_metadata.csv from registry.pickle.

### Export types
There are three different export types which can be specified with the optional `--exporttype` flag. These modify the metadata CSV file output (the output of step 2 above).

#### FRDR
This is the default export type if no type is specified.
`--exporttype frdr` has the following columns:

- **id**: Crossref Funder ID (DOI)
- **country_code**: Geonames ID
-  **name_en**: prefLabel in Crossref Funder Registry or name_en from override file
-  **name_fr**: prefLabel in Crossref Funder Registry or name_fr 

This export includes all funders except:
	- funders with termstatus "Deprecated"
	- funders that have been superseded by a new funder

#### Full
`--exporttype full` includes all columns from the Crossref Funder Registry. It includes all funders regardless of termstatus.

#### Curation - Canada
`--exporttype curation_ca` only includes Canadian funders. This export has additional processing applied to support curation of the override file for Canadian entries, including:

- separating out labels by language to support usage in bilingual applications
- adding related ROR IDs
- replacing geonames URIs for Canada and the provinces/territories with names

To add related ROR IDs, the name of the ROR data file must be specified with `--rordata`. This file should be placed in the `registry_data` folder.

Usage example: `python FundrefRDFParser.py --metadatacsv --exporttype curation_ca --rordata 2021-09-23-ror-data.json`


## Workflow Documentation
- [ROR: Workflows for FRDR](https://docs.google.com/document/d/1-5n_A9Wo9OzVdQ6OYk0vIKF0khsY6iQu3REMBGWP5K4/edit#)
- [Crossref Funder Registry: Workflows for FRDR](https://docs.google.com/document/d/1swDZqb94xdmpEnHjKakF_DI_mXHRVIYcsodEBRPG1r0/edit#)









