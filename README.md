# GoogleSheetsSpellbook

This repo contains scripts that generate the [mints review sheet](https://docs.google.com/spreadsheets/d/1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0/edit?gid=1337774973#gid=1337774973) for [GENEPIO](https://github.com/genepio/genepio) with the [Google Sheets API Python Client](https://developers.google.com/workspace/sheets/api/quickstart/python).

<img width="1794" height="934" alt="image" src="https://github.com/user-attachments/assets/832a417d-e954-492e-8b54-d38a0e744171" />


The script ```check_mints.py``` autogenerates the ```Mints review``` tab of the [mints sheet](https://docs.google.com/spreadsheets/d/1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0/edit?gid=1337774973#gid=1337774973). First, it gathers all the minted terms from the ```2022-2025``` tabs into the ```mints_review``` tab. Next it checks whether or not each minted term has been merged into [genepio.owl](https://github.com/GenEpiO/genepio/blob/master/src/ontology/genepio.owl) based on the [ROBOT export](https://robot.obolibrary.org/export.html) table ```genepio_terms.csv```. Finally, it checks whether each mint is described in any of the Google Sheets versions of ROBOT tables and curation sheets requested in ```input.json```, and records the name of the spreadsheet tab where it is found.

It also tabulates the types of matches for each subset and reports them to the ```Mints review legend``` tab of the [mints sheet](https://docs.google.com/spreadsheets/d/1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0/edit?gid=1337774973#gid=1337774973):
<img width="490" height="610" alt="image" src="https://github.com/user-attachments/assets/b7434a1b-9b51-40ba-b412-4ad2743a544a" />

This app is called ```mints-tracker``` and is part of the Google Cloud Console project ```ontology-mints-tracker```. It is an unverified app in Testing mode and should be available to external users, but has yet to be tested on a computer other than ```tamarisk```.

**How to run this code from the shell:**

1. Navigate to ```genepio/src/ontology```. From there, prepare a new release like this: 

```
git pull # fetch the latest version of GENEPIO
git checkout -b release-2026-03-17 # checkout a new branch in preparation for creating a new release
sudo docker ps # check that Docker is running
sudo docker pull obolibrary/odkfull # pull the ODK docker image
sudo sh run.sh robot --version # check that ODK is running
sudo sh run.sh make prepare_release -B # regenerate genepio-merged.owl by preparing a release (*don't push this release to the repo)
```

2. Run ROBOT export to get ```genepio-merged.owl``` terms in a CSV file called ```genepio_terms.csv```:

```
sudo sh run.sh robot export --input genepio-merged.owl   --header "ID|LABEL|SYNONYMS"   --export genepio_terms.csv
```

3. Copy ```genepio_terms.csv``` into GoogleSheetsSpellbook.

4. Within the GoogleSheetsSpellbook directory, activate the conda environment and run the Python script to update the Mints Review tab online:
```
conda activate google-mint
python3 check_mints.py --input input.json
``` 

5. Finally, check that the ```mints_review``` tab of the GENEPIO Mints Google sheet is updated correctly.

**Requirements:**
* Follow the directions at: https://developers.google.com/workspace/sheets/api/quickstart/python.
* Install all required packages using Conda: the environment.yaml file contains everything you will need and creates an environment called ```google-mint```.
* This code was developed using Python 3.13.11 and Ubuntu 20.04.
* I had to add myself as a test user to gain access with ```quickstart.py``` as in [the tutorial](https://developers.google.com/workspace/sheets/api/quickstart/python).
* Remember to enable the Google Sheets API at https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=88442894636.
* ```credentials.json``` is stored locally and not shown in this repo in order to keep the client secret a secret...
* ~~ADC must be in place for functions.py to work. See [Issue #1](https://github.com/miseminger/GoogleSheetsSpellbook/issues/1) for directions.~~


**Useful links:**

* [Charlie and Ivan's Mint QC script](https://github.com/cbarcl01/mint_qc_script)
* [Google Sheets API guide with Python snippets](https://developers.google.com/workspace/sheets/api/guides/concepts) - A1 notation for spreadsheet data ranges is explained on the first page
* [GitHub repo for the Google API Python Client](https://github.com/googleapis/google-api-python-client/tree/main/docs)
* ~~https://www.thebricks.com/resources/guide-how-to-edit-google-sheets-with-python~~ (don't use this: ```gspread``` is old)

