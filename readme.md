# FRDR Controlled Vocabularies

This project provides tools to parse ROR and Crossref Funder Registry data into CSV files for FRDR.

## Research Organization Registry (ROR)
`RORJsonParser.py` parses the ROR data dump (JSON) to a CSV file for use in FRDR affiliation metadata. This output file has the columns  *id*, *primary_name*, amd *additional_names*.

Usage: `python RORJsonParser.py --file ror-data.json`

## Crossref Funder Registry
`FundrefRDFParser.py` parses the Crossref Funder Registry RDF file to a CSV file for use in FRDR funding metadata.

### Flags
Usage: `python FundrefRDFParser.py --graphpickle --metadatacsv`

- Step 1: `--graphpickle`: Generate registry.pickle from registry.rdf.
- Step 2: `--metadatacsv`: Generate funder_metadata.csv from registry.pickle.

Optional `--exporttype` argument can be used to change the output of step 2 (`--metadatacsv` flag):

- `--exporttype frdr`: Only include the columns *id*, *primary_name*, *additional_names*, *dcterms_created*, and *dcterms_modified*. Do not include funders with termstatus "Deprecated" or funders that have been superseded by a new funder.
- `--exporttype canada`: Optional processing for Canadian funders, including:
    - separating out labels by language to support usage in bilingual applications
    - adding related ROR IDs
    - replacing geonames URIs for Canada and the provinces/territories with names

## Workflow Documentation
- [ROR: Workflows for FRDR](https://docs.google.com/document/d/1-5n_A9Wo9OzVdQ6OYk0vIKF0khsY6iQu3REMBGWP5K4/edit#)
- [Crossref Funder Registry: Workflows for FRDR](https://docs.google.com/document/d/1swDZqb94xdmpEnHjKakF_DI_mXHRVIYcsodEBRPG1r0/edit#)









