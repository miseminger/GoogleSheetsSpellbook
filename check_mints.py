''''
This script fetches data from the GENEPIO mints sheet, 
compares it to genepio-edit.owl, and fills in a spreadsheet column
identifying whether a given mint has been added to the OWL file or not yet.
'''

import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from functions import *


# The ID and range of the mints spreadsheet.
MINTS_SPREADSHEET_ID = "1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0" #mints sheet
SAMPLE_RANGE_NAME = "2025!A3:E" # fetch columns A-E from the 2025 sheet
MINTS_COLUMNS = ['IRI', 'label', 'creator (GitHub username)', 'reservation date', 'subset'] # names of columns A-E in order


if __name__ == "__main__":

  # read 2025 mints sheet into a df
  mints_list = get_values(MINTS_SPREADSHEET_ID, SAMPLE_RANGE_NAME).get("values", [])
  mints_df = pd.DataFrame(mints_list, columns=MINTS_COLUMNS) # convert to a pandas df
  mints_df = mints_df[mints_df['label'].notna()] # remove rows with an IRI but no label
  print("mints_df")
  print(mints_df)

  # read in TSV of terms that are already in GENEPIO
  # this TSV must have columns titled ['IRI', 'label']
  genepio_edit_df = pd.read_csv("genepio_edit_terms.tsv", sep='\t', header=0)
  genepio_edit_df['in_GENEPIO'] = 'YYYY' # add column to be used in merge
  genepio_edit_df = genepio_edit_df.drop(columns=['type'])# drop 'type' column
  print("genepio_edit_df")
  print(genepio_edit_df)

  # merge mints sheet with genepio-edit sheet
  merged_df = pd.merge(mints_df, genepio_edit_df, on=['IRI', 'label'], how='left')
  print("merged_df")
  print(merged_df)
  # final df should be the same size as mints_df!

  print(merged_df[merged_df['in_GENEPIO'].notna()])
