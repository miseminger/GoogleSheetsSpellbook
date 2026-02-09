# GoogleSheetsSpellbook

This repo is for storing practice with the Google API Python Client. The current use case is for managing the mints sheet for [GENEPIO](https://github.com/genepio/genepio), but may branch out into other applications in the future.

**How to run this code from the shell:**

```conda activate google-mint```
```python3 check_mints.py --input input.json``` 


**Notes**
* The app is called ```mints-tracker``` and is part of the project ```ontology-mints-tracker```.
* It is available to external users--but for the moment only external users who I have granted permission to as the app is under Testing status and has not been verified by Google yet. (Add new users as needed under the Audience tab.)

**Requirements:**
* Follow the directions at: https://developers.google.com/workspace/sheets/api/quickstart/python.
* Install all required packages using Conda: the environment.yaml file contains everything you will need and creates an environment called ```google-mint```.
* This code was developed using Python 3.13.11 and Ubuntu 20.04.
* I had to add myself as a test user to gain access with ```quickstart.py``` as in [the tutorial](https://developers.google.com/workspace/sheets/api/quickstart/python).
* Remember to enable the Google Sheets API at https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=88442894636.
* ```credentials.json``` is stored locally and not shown in this repo in order to keep the client secret a secret...
* ADC must be in place for functions.py to work. See [Issue #1](https://github.com/miseminger/GoogleSheetsSpellbook/issues/1) for directions.

**Useful links:**

* [Charlie and Ivan's Mint QC script](https://github.com/cbarcl01/mint_qc_script)
* [Google Sheets API guide with Python snippets](https://developers.google.com/workspace/sheets/api/guides/concepts) - A1 notation for spreadsheet data ranges is explained on the first page
* [GitHub repo for the Google API Python Client](https://github.com/googleapis/google-api-python-client/tree/main/docs)
* ~~https://www.thebricks.com/resources/guide-how-to-edit-google-sheets-with-python~~ (don't use this: ```gspread``` is old)

