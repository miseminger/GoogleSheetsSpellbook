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

from functions import batch_get_values, update_values, compare_terms, count_matches_by_subset, get_hyperlinks_list, get_hyperlinks_df, update_merge_status

mints_review_df_columns = ["IRI",	"label", "creator (GitHub username)",	"reservation date",	"subset",	"In genepio-merged.owl?",	"In GENEPIO ROBOT?",	"Tab location in GENEPIO ROBOT",	"In GENEPIO curation?",	"Tab location in GENEPIO curation sheet"] #,	"Notes"

def parse_args():
    
    parser = argparse.ArgumentParser(
        description='Updates the mints review sheet.')
    parser.add_argument('--input', type=str, default=None, required=True,
                        help='Path to the JSON file of spreadsheet metadata')
 
    return parser.parse_args()



def get_multitab_df_robot(input_dict, creds):
  spreadsheet_id = input_dict.pop("SPREADSHEET_ID")
  print("Processing: ", spreadsheet_id)
  range_names = ["spec_field", "spec_field (retired)", "identifiers (draft)", "SSSOM-Import-Overlay", "spec_enum", "genes", "temp mint", "deprecation_import", "imports (temp)", "I#72", "Sheet25", "Copy of Rhi Term List", "DEPRECATE (To-dos)"]
  column_names = ['NCIT_containing_entry', 'column_name', 'tab']
  start_row = input_dict.pop("START_ROW")
  rename_columns = input_dict.pop("RENAME_COLUMNS")
  values = batch_get_values(spreadsheet_id, range_names, creds)
  # initialize empty df
  multitab_df = pd.DataFrame(columns=column_names)

  # fill in empty df sheet by sheet
  for sheet in range(len(values['valueRanges'])):
      tab = values['valueRanges'][sheet]['range'].split('!')[0] # save the name of the tab, eg. '2023_error_curation (Charlie)'
      # replace spaces with underscores in tab name 
      tab = tab.replace(" ", "_")
      #print("    " + tab)
      # collect the data in that tab in a pandas df
      sheet_data = values['valueRanges'][sheet]['values']
      sheet_df = pd.DataFrame(sheet_data, columns=sheet_data[0])
      sheet_df = sheet_df[start_row:] # leave off ROBOT instructions
      # replace '\n' in column names with a space
      sheet_df.columns = [colname.replace('\n', ' ') for colname in sheet_df.columns.tolist()]
      #print("sheet_df.columns", sheet_df.columns)

      for column in sheet_df.columns:
        mini_df = pd.DataFrame(columns=column_names)
        mini_df['NCIT_containing_entry'] = sheet_df[column][sheet_df[column].str.contains('NCIT')]
        mini_df['column_name'] = column
        mini_df['tab'] = tab
        if mini_df.shape[0] > 0:
            print(mini_df)
        # append sheet_df to the spreadsheet df
        multitab_df = pd.concat([multitab_df, mini_df])

  return multitab_df



if __name__ == "__main__":

  args = parse_args()

  with open(args.input) as fp:
    RESOURCE_DICT = json.load(fp)

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


# read in genepio-ROBOT sheets
robot_df = get_multitab_df_robot(RESOURCE_DICT["GENEPIO_ROBOT_SPREADSHEET"], creds)

print(robot_df.shape[0])
print(robot_df.columns)
print(robot_df)

robot_df.to_csv("ncit_in_robot.tsv", sep='\t')