''''
This script fetches data from the GENEPIO mints sheet, 
compares it to genepio-edit.owl, and fills in spreadsheet columns
identifying whether a given mint has been added to the OWL file, 
ROBOT tables or curation tables or not yet.
'''

import os.path
import pandas as pd
import numpy as np
import json
import argparse
import matplotlib.pyplot as plt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from functions import get_multitab_df, update_values, compare_terms, count_matches_by_subset, get_hyperlinks_list, get_hyperlinks_df, update_merge_status

mints_review_df_columns = ["IRI",	"label", "creator (GitHub username)",	"reservation date",	"subset",	"In genepio.owl?",	"In GENEPIO ROBOT?",	"Tab location in GENEPIO ROBOT",	"In GENEPIO curation?",	"Tab location in GENEPIO curation sheet"] #,	"Notes"

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
      print("requesting new token")
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
  #print(duplicated_IRIs)

  # read in CSV of terms that are already in GENEPIO (from ROBOT export of genepio.owl)
  # this CSV must have columns titled ['IRI', 'LABEL']
  genepio_df = pd.read_csv("genepio_terms.csv", sep=',', header=0)
  # rename columns to match mints sheet
  genepio_df = genepio_df.rename(columns={"ID": "IRI", "LABEL": "label", "SYNONYMS": "alternative label"})
  # drop 'SYNONYMS' column
  #genepio_df = genepio_df.drop(columns=['SYNONYMS'])
  # merge mints sheet with genepio sheet
  mints_review_df = compare_terms(mints_df, genepio_df, 'In genepio.owl?', None)
  duplicated_IRIs = mints_review_df[mints_review_df.duplicated(subset=["IRI"])]
  print(str(duplicated_IRIs.shape[0]) + " duplicate IRIs detected in the Mints_review sheet after GENEPIO check")

  # read in genepio-ROBOT sheets
  robot_df = get_multitab_df(RESOURCE_DICT["GENEPIO_ROBOT_SPREADSHEET"], creds)
  robot_df = robot_df[robot_df['Ontology ID'].astype(str).str.contains("GENEPIO")] # remove rows with no IRI
  robot_df = robot_df[robot_df['label'].notna()] # remove rows where the label is NaN, keep rows where the label is ''
  # rename "Ontology ID" column to "IRI" to match mints sheet
  robot_df = robot_df.rename(columns={"Ontology ID": "IRI"}) 
  # check for duplicate IRIs
  robot_duplicated_IRIs = robot_df[robot_df.duplicated(subset=["IRI"])]
  print(str(robot_duplicated_IRIs.shape[0]) + " duplicate IRIs detected in the ROBOT sheet")


  # merge mints sheet with genepio-ROBOT sheet
  mints_review_df = compare_terms(mints_review_df, robot_df, 'In GENEPIO ROBOT?', "Tab location in GENEPIO ROBOT")
  # check for duplicate IRIs again
  duplicated_IRIs = mints_review_df[mints_review_df.duplicated(subset=["IRI"])]
  print(str(duplicated_IRIs.shape[0]) + " duplicate IRIs detected in the Mints_review sheet after ROBOT check")


  ## check if mints are in a curation sheet
  curation_df = pd.DataFrame(columns=["Ontology ID", "label", "alternative label", "tab"])
  for spreadsheet in RESOURCE_DICT["CURATION_SHEETS"]:
    # get multitab df for each curation sheet
    multitab_curation_df = get_multitab_df(RESOURCE_DICT["CURATION_SHEETS"][spreadsheet], creds)
    # concatenate multitab dfs into one long df
    curation_df = pd.concat([curation_df, multitab_curation_df])

  # rename "Ontology ID" column to "IRI" to match mints sheet
  curation_df = curation_df.rename(columns={"Ontology ID": "IRI"}) 
  # restrict columns to those that should be merged into mints_review
  curation_df = curation_df[["IRI", "label", "tab"]] 
  # merge with mints_review
  mints_review_df = compare_terms(mints_review_df, curation_df, "In GENEPIO curation?", "Tab location in GENEPIO curation sheet")
  duplicated_IRIs = mints_review_df[mints_review_df.duplicated(subset=["IRI"])]
  print(str(duplicated_IRIs.shape[0]) + " duplicate IRIs detected in the Mints_review sheet after curation sheet check")

  # replace all NaN values with empty strings
  mints_review_df = mints_review_df.fillna('')
  # add hyperlinks to ROBOT tabs - no extra columns added here
  mints_review_df = get_hyperlinks_df(mints_review_df, "Tab location in GENEPIO ROBOT")
  # make sure columns are in order
  mints_review_df = mints_review_df[mints_review_df_columns]
  # add hyperlinks to curation tabs - some extra columns added here on the RHS
  mints_review_df = get_hyperlinks_df(mints_review_df, "Tab location in GENEPIO curation sheet")
  # drop duplicated rows
  mints_review_df = mints_review_df.drop_duplicates()
  # convert df back to nested list
  mints_review_df_values = mints_review_df.values.tolist() 
  
  # update Mints_review tab
  update_values(mints_review_sheet_id, "Mints review!A3:P", "USER_ENTERED", mints_review_df_values, creds)
  #update_values("1Ts4nU6vQRwmnXQz0HzBM7Wz3N4tOVxo9F3-nH6cp06A", "Mints review!A3:P", "USER_ENTERED", mints_review_df_values, creds)

  # get match counts table 
  match_counts_df = count_matches_by_subset(mints_review_df, "In genepio.owl?", "In GENEPIO ROBOT?", "In GENEPIO curation?")

  # make horizontal bar plot of number of terms not found for each subset
  savefile = "subset_plot.png"
  ax = match_counts_df['no_match_counts'].plot.barh(color='red')
  plt.title("Mints without matches", fontweight='bold')
  plt.ylabel("Subset", fontweight='bold')
  plt.xlabel("Number of terms", fontweight='bold')
  plt.tight_layout()
  ax.invert_yaxis()
  for p in ax.patches:
      ax.annotate(f"{p.get_width()}", (p.get_width() + p.get_height()/200, p.get_center()[1]), va="center", ha="left")
  #plt.bar_label()
  plt.savefig(savefile)
  print("Subset plot saved as: " + savefile)

  # update Mints review legend tab with match type counts table
  match_counts_df = match_counts_df.reset_index()
  match_counts_df_values = match_counts_df.values.tolist() 
  update_values(mints_review_sheet_id, "Mints review legend!G2:I", "USER_ENTERED", match_counts_df_values, creds)

  # get set of IDs for terms merged into GENEPIO
  merged_mask = (mints_review_df['In genepio.owl?']==('id_match' or 'id_and_label_match'))
  merged_ids = set(mints_review_df['IRI'][merged_mask].tolist())

  # go through the Mints sheets and update the "merged" column
  #input_dict = RESOURCE_DICT["MINTS_SPREADSHEET"]
  #mints_sheet_id = input_dict.pop("SPREADSHEET_ID")
  mints_sheet_range_names = ["2022", "2023", "2024!1:1070", "2025"] #input_dict.pop("RANGE_NAMES")
  start_row = 1 #input_dict.pop("START_ROW")
  for range_name in mints_sheet_range_names:
    print("Updating 'merged' status for: ", range_name)
    update_merge_status(mints_review_sheet_id, range_name, start_row, merged_ids, creds)
