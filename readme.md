# FRDR Controlled Vocabularies

This project provides tools to parse ROR and Crossref Funder Registry data into CSV files for FRDR.

## Research Organization Registry (ROR)
`RORJsonParser.py` parses the ROR data dump (JSON) to a CSV file for use in FRDR affiliation metadata.

Usage: `python RORJsonParser.py --file ror-data.json`

## Crossref Funder Registry
`FundrefRDFParser.py` parses the Crossref Funder Registry RDF file to a CSV file for use in FRDR funding metadata.

Usage: `python FundrefRDFParser.py --graphpickle --metadatacsv`

Optional processing for Canadian funders (`--canada` flag) includes:

- separating out labels by language to support usage in bilingual applications
- adding related ROR IDs
- replacing geonames URIs for Canada and the provinces/territories with names

## Workflow Documentation
- [ROR: Workflows for FRDR](https://docs.google.com/document/d/1-5n_A9Wo9OzVdQ6OYk0vIKF0khsY6iQu3REMBGWP5K4/edit#)
- [Crossref Funder Registry: Workflows for FRDR](https://docs.google.com/document/d/1swDZqb94xdmpEnHjKakF_DI_mXHRVIYcsodEBRPG1r0/edit#)









