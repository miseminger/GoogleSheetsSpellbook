''''
This script fetches data from the GENEPIO mints sheet, 
compares it to genepio-edit.owl, and fills in a spreadsheet column
identifying whether a given mint has been added to the OWL file or not yet.
'''

import os.path
import pandas as pd
import numpy as np

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from functions import *


# The ID and range of the mints spreadsheet.

MINTS_SPREADSHEET_ID = "1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0" # mints sheet
MINTS_RANGE_NAME = "2025!A3:E" # fetch columns A-E from the 2025 sheet
MINTS_COLUMNS = ['IRI', 'label', 'creator (GitHub username)', 'reservation date', 'subset'] # names of columns A-E in order

GENEPIO_ROBOT_SPREADSHEET_ID = "1L1051tGcWerbCJkFPnBTe6gQ_9sYuthvmNPNf7Ljtq4" # ROBOT sheet
GENEPIO_ROBOT_RANGE_NAME = "spec_field (new)!A4:B" # fetch first two columns
GENEPIO_ROBOT_ARCHIVAL_RANGE_NAMES = ''

CURATION_SHEET_2023 = "1s6FB9EyPWYBgssIU9a9AKATEfZnMdixwvrGhBXUHAVk" # GENEPIO 2023 Curation Tables
CURATION_SHEET_2024 = "14r_qlNJUCGJ_59MA3MR0x4JObsYpQI_2AFJGMu_wyl4" # GENEPIO 2024 Curation Tables


if __name__ == "__main__":

  # read 2025 mints sheet into a df
  mints_list = get_values(MINTS_SPREADSHEET_ID, MINTS_RANGE_NAME).get("values", [])
  mints_df = pd.DataFrame(mints_list, columns=MINTS_COLUMNS) # convert to a pandas df
  mints_df = mints_df[mints_df['label'].notna()] # remove rows with an IRI but no label
  print("mints_df")
  print(mints_df)

  # read in TSV of terms that are already in GENEPIO
  # this TSV must have columns titled ['IRI', 'label']
  genepio_edit_df = pd.read_csv("genepio_edit_terms.tsv", sep='\t', header=0)
  genepio_edit_df['In genepio-edit.owl?'] = 'YES' # add column to be used in merge
  genepio_edit_df = genepio_edit_df.drop(columns=['type'])# drop 'type' column
  print("genepio_edit_df")
  print(genepio_edit_df)

  # merge mints sheet with genepio-edit sheet
  merged_df = pd.merge(mints_df, genepio_edit_df, on=['IRI', 'label'], how='left')
  # final df should be the same size as mints_df!

  print(merged_df[merged_df['In genepio-edit.owl?'].notna()])

  # read in genepio-ROBOT sheet: spec_field (new)
  robot_list = get_values(GENEPIO_ROBOT_SPREADSHEET_ID, GENEPIO_ROBOT_RANGE_NAME).get("values", [])
  robot_df = pd.DataFrame(robot_list, columns=['IRI', 'label']) # convert to a pandas df
  robot_df = robot_df.replace(r'^\s+$', np.nan, regex=True) # replace empty strings with nan
  robot_df = robot_df[robot_df['IRI'].str.contains("GENEPIO")] # remove rows with no IRI
  robot_df = robot_df[robot_df['label'].notna()] # remove rows with no label

  # check if mints are in genepio-ROBOT sheet: spec_field (new)
  robot_df['In GENEPIO ROBOT?'] = 'YES' # add column to be used in merge
  # merge mints sheet with genepio-ROBOT sheet
  merged_df_2 = pd.merge(merged_df, robot_df, on=['IRI', 'label'], how='left')
  print("merged_df_2")
  print(merged_df_2)
  # final df should be the same size as mints_df!

  # print out any terms that are in the ROBOT file
  print(merged_df_2[merged_df_2['In GENEPIO ROBOT?'].notna()])

  # replace all NaN values with empty strings
  merged_df_2 = merged_df_2.fillna('')

  # update the Mints_review spreadsheet in Google Sheets
  values2 = merged_df_2.values.tolist() # convert df back to nested list
  print(values2)
  update_values(MINTS_SPREADSHEET_ID, "Mints review!A3:K", "RAW", values2)
