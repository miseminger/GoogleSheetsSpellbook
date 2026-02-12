''''
This script fetches data from the GENEPIO mints sheet, 
compares it to genepio-edit.owl, and fills in a spreadsheet column
identifying whether a given mint has been added to the OWL file or not yet.
'''

import os.path
import pandas as pd
import numpy as np
import json
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from functions import get_multitab_df, update_values

mints_review_df_columns = ["IRI",	"label", "creator (GitHub username)",	"reservation date",	"subset",	"In genepio.owl?",	"In GENEPIO ROBOT?",	"Tab location in GENEPIO ROBOT",	"In GENEPIO curation?",	"Tab location in GENEPIO curation"] #,	"Notes"

def parse_args():
    
    parser = argparse.ArgumentParser(
        description='Updates the mints review sheet.')
    parser.add_argument('--input', type=str, default=None, required=True,
                        help='Path to the JSON file of spreadsheet metadata')
 
    return parser.parse_args()

if __name__ == "__main__":

  args = parse_args()

  with open(args.input) as fp:
    RESOURCE_DICT = json.load(fp)

  mints_review_sheet_id = "1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0"

  # If modifying these scopes, delete the file token.json.
  SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  #try:
  #  service = build("sheets", "v4", credentials=creds)

  #  # Call the Sheets API
  #  sheet = service.spreadsheets()


  # read all mints sheets into a df
  mints_df = get_multitab_df(RESOURCE_DICT["MINTS_SPREADSHEET"], creds) 
  mints_df = mints_df.drop(columns=['tab'])# drop 'tab' column
  print(mints_df.shape)

  # check for duplicated IRIs with different labels
  duplicated_IRIs = mints_df[mints_df.duplicated(subset=["IRI"])]
  print(str(duplicated_IRIs.shape[0]) + " duplicate IRIs detected in the Mints sheets")
  #print(duplicated_IRIs) # 41 show at baseline and have already been solved (see 2024 Mints sheet)
  

  # read in CSV of terms that are already in GENEPIO (from ROBOT export of genepio.owl)
  # this CSV must have columns titled ['IRI', 'LABEL']
  genepio_df = pd.read_csv("genepio_terms.csv", sep=',', header=0)
  genepio_df['In genepio.owl?'] = 'yes' # add column to be used in merge
  # rename columns to match mints sheet
  genepio_df = genepio_df.rename(columns={"ID": "IRI", "LABEL": "label"})
  # drop 'SYNONYMS' column
  genepio_df = genepio_df.drop(columns=['SYNONYMS'])

  # merge mints sheet with genepio sheet
  mints_review_df = pd.merge(mints_df, genepio_df, on=['IRI', 'label'], how='left')
  # final df should be the same size as mints_df!

  #print(merged_df[merged_df['In genepio.owl?'].notna()])

  # read in genepio-ROBOT sheets
  robot_df = get_multitab_df(RESOURCE_DICT["GENEPIO_ROBOT_SPREADSHEET"], creds)
  robot_df = robot_df[robot_df['Ontology ID'].str.contains("GENEPIO")] # remove rows with no IRI
  robot_df = robot_df[robot_df['label'].notna()] # remove rows with no label
  robot_df['In GENEPIO ROBOT?'] = 'yes' # add column to be used in merge
  # rename "Ontology ID" column to "IRI" to match mints sheet
  robot_df = robot_df.rename(columns={"Ontology ID": "IRI", "tab": "Tab location in GENEPIO ROBOT"})

  # merge mints sheet with genepio-ROBOT sheet
  mints_review_df = pd.merge(mints_review_df, robot_df, on=['IRI', 'label'], how='left')
  #print("mints_review_df")
  #print(mints_review_df)
  # final df should be the same size as mints_df!

  # print out any terms that are in the ROBOT file
  #print("terms in ROBOT spec field (new)")
  #print(mints_review_df[mints_review_df['In GENEPIO ROBOT?'].notna()])

  ## check if mints are in a curation sheet
  curation_2023_df = get_multitab_df(RESOURCE_DICT["CURATION_SHEET_2023_SPREADSHEET"], creds)
  curation_2024_df = get_multitab_df(RESOURCE_DICT["CURATION_SHEET_2024_SPREADSHEET"], creds)
  #madeline_mpox_curation_df = get_multitab_df(RESOURCE_DICT["MADELINE_MPOX_ROBOT_SPREADSHEET"], creds)
  # concatenate curation sheets into one long df
  curation_df = pd.concat([curation_2023_df, curation_2024_df])
  #curation_df = pd.concat([curation_df, madeline_mpox_curation_df])
  # add "In GENEPIO curation?" tab
  curation_df["In GENEPIO curation?"] = 'yes'
  # rename "Ontology ID" column to "IRI" to match mints sheet
  curation_df = curation_df.rename(columns={"Ontology ID": "IRI", "tab": "Tab location in GENEPIO curation"})
  # restrict columns to those that should be merged into mints_review
  curation_df = curation_df[["IRI", "label", "In GENEPIO curation?", "Tab location in GENEPIO curation"]]
  # combine duplicate rows and transform "Tab location in GENEPIO curation" into a comma-separated list
  curation_df = curation_df.groupby(["IRI", "label", "In GENEPIO curation?"]).agg({"Tab location in GENEPIO curation": ', '.join}).reset_index()
  #print(curation_df[curation_df["Tab location in GENEPIO curation"].str.contains(",")])

  # take out problematic rows to look at separately
  # take all rows with IRIs that don't contain "GENEPIO"
  # take all rows without labels

  # merge with mints_review
  mints_review_df = pd.merge(mints_review_df, curation_df, on=['IRI', 'label'], how='left')

  ## troubleshooting "2023_mints_wastewater (Charlie)"
  #curation_2023_df = curation_2023_df.sort_values(by=["Ontology ID"])
  #curation_2023_values = curation_2023_df.values.tolist()
  #update_values(CURATION_SHEET_2023, "Madeline_error_review_2026", "RAW", curation_2023_values)

  # update the Mints_review spreadsheet in Google Sheets
  # replace all NaN values with empty strings
  mints_review_df = mints_review_df.fillna('')
  # fill in 'no' in the absence of 'yes'
  mints_review_df['In genepio.owl?'] = mints_review_df['In genepio.owl?'].where(mints_review_df['In genepio.owl?'] == 'yes', 'no')
  mints_review_df['In GENEPIO ROBOT?'] = mints_review_df['In GENEPIO ROBOT?'].where(mints_review_df['In GENEPIO ROBOT?'] == 'yes', 'no')
  mints_review_df['In GENEPIO curation?'] = mints_review_df['In GENEPIO curation?'].where(mints_review_df['In GENEPIO curation?'] == 'yes', 'no')
  # make sure columns are in order
  mints_review_df = mints_review_df[mints_review_df_columns]
  #print(mints_review_df)
  #print(mints_df)
  # convert df back to nested list
  mints_review_df_values = mints_review_df.values.tolist() 
  
  # update Mints_review tab
  update_values(mints_review_sheet_id, "Mints review!A3:K", "RAW", mints_review_df_values, creds)
