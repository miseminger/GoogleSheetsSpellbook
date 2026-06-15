''''
This script fetches data from the GENEPIO mints sheets and mints_review sheets, and updates the 
"merged" column of each mints sheet to TRUE or FALSE based on the "In genepio.owl?" column of the 
mints review sheet. A mint is recorded as "merged"==TRUE if "In genepio.owl?" contains the string
"id_match" or the string "id_and_label_match" and is otherwise FALSE.
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

from functions import get_multitab_df, batch_get_values, update_values, compare_terms, count_matches_by_subset, get_hyperlinks_list, get_hyperlinks_df

mints_review_df_columns = ["IRI",	"label", "creator (GitHub username)",	"reservation date",	"subset",	"In genepio.owl?",	"In GENEPIO ROBOT?",	"Tab location in GENEPIO ROBOT",	"In GENEPIO curation?",	"Tab location in GENEPIO curation sheet"] #,	"Notes"

def parse_args():
    
    parser = argparse.ArgumentParser(
        description='Updates the mints review sheet.')
    parser.add_argument('--input', type=str, default=None, required=True,
                        help='Path to the JSON file of spreadsheet metadata')
 
    return parser.parse_args()

if __name__ == "__main__":

  args = parse_args()

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

 
  def get_sheet_df(spreadsheet_id, range_names, start_row, creds):
  
    values = batch_get_values(spreadsheet_id, range_names, creds)

    for sheet in range(len(values['valueRanges'])):
        tab = values['valueRanges'][sheet]['range'].split('!')[0] # save the name of the tab, eg. '2023_error_curation (Charlie)'
        # replace spaces with underscores in tab name 
        tab = tab.replace(" ", "_")
        print("    " + tab)
        # collect the data in that tab in a pandas df
        sheet_data = values['valueRanges'][sheet]['values']
        sheet_df = pd.DataFrame(sheet_data, columns=sheet_data[0])
        sheet_df = sheet_df[start_row:] # leave off columns in df body
    
    return sheet_df

  mints_sheet_id = "1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0"

  # fetch merged GENEPIO IDs from Mints sheet
  # read Mints review sheet into a pandas df
  merged_ids_df = get_sheet_df(mints_sheet_id, "Mints review!A1:P", 1, creds)
  # get merged IDs found in the Mints review sheet as a set
  # (could also just take these directly from genepio_terms.csv)
  merged_mask = (merged_ids_df['In genepio.owl?']==('id_match' or 'id_and_label_match'))
  merged_ids = set(merged_ids_df['IRI'][merged_mask].tolist())

  def update_merge_status(mints_sheet_id, mints_sheet_range_names, start_row, merged_ids_set, creds):
    # fetch a mints sheet
    mints_sheet_df = get_sheet_df(mints_sheet_id, mints_sheet_range_names, start_row, creds)
    # set MERGED==FALSE as default
    mints_sheet_df["merged"] = 'FALSE'
    # iterate through IDs in merged_ids_set
    for merged_id in merged_ids_set:
      # if the mints sheet contains a merged_id, set "merged"=="TRUE" for that ID
      mints_sheet_df.loc[mints_sheet_df['IRI']==merged_id, "merged"] = "TRUE"
    #print(mints_sheet_df[mints_sheet_df["merged"]=="TRUE"])
    # convert df back to nested list
    mints_sheet_df_values = mints_sheet_df.values.tolist() 
    # add column names as first list in nested list
    print("columns_list")
    columns_list = [list(mints_sheet_df.columns)]
    mints_sheet_df_values = columns_list + mints_sheet_df_values
    print(columns_list)
    print("")
    print("mints_sheet_df_values")
    print(mints_sheet_df_values[:3])
    # update mints sheet "merged" column online
    update_values(mints_sheet_id, mints_sheet_range_names, "USER_ENTERED", mints_sheet_df_values, creds)

  update_merge_status(mints_sheet_id, "2022!A1:P", 1, merged_ids, creds)