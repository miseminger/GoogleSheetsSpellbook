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


# The ID and range of the Mints spreadsheet
MINTS_SPREADSHEET_ID = "1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0" # mints sheet id
MINTS_RANGE_NAMES = ["2024", "2025"] #, "2024!A2:E", "2023!A2:E", "2022!A2:E"] # fetch columns A-E from the 2022-2026 sheets
MINTS_COLUMN_NAMES = ['IRI', 'label', 'creator (GitHub username)', 'reservation date', 'subset'] # names of columns A-E in order

# GENEPIO ROBOT Table
GENEPIO_ROBOT_SPREADSHEET_ID = "1L1051tGcWerbCJkFPnBTe6gQ_9sYuthvmNPNf7Ljtq4" # ROBOT sheet
GENEPIO_ROBOT_RANGE_NAME = "spec_field (new)!A4:B" # fetch first two columns
GENEPIO_ROBOT_ARCHIVAL_RANGE_NAMES = ''

# GENEPIO 2023 Curation Tables
CURATION_SHEET_2023 = "1s6FB9EyPWYBgssIU9a9AKATEfZnMdixwvrGhBXUHAVk" 
CURATION_SHEET_2023_RANGE_NAMES = ["2023_mints_wastewater_terms (Charlie)", "2023_manual_curation (Charlie)"] # don't search "2023_mints_wastewater (Charlie)" until further notice
CURATION_SHEET_2023_COLUMN_NAMES = ['Ontology ID','label', 'alternative label']

# GENEPIO 2024 Curation Tables
CURATION_SHEET_2024 = "14r_qlNJUCGJ_59MA3MR0x4JObsYpQI_2AFJGMu_wyl4" 
CURATION_SHEET_2024_RANGE_NAMES = ["2024_hAMRonization", "2024_GRDI", "2024_HPAI", "2024_QC", "2024_CanCOGen", "2024_Pathoplexus", "2024_MPOX", "2024_wastewater"]
CURATION_SHEET_2024_COLUMN_NAMES = ['Ontology ID','label', 'alternative label']


if __name__ == "__main__":

  # read 2023 mints sheet into a df
  #mints_list = get_values(MINTS_SPREADSHEET_ID, MINTS_RANGE_NAMES).get("values", [])
  #mints_df = pd.DataFrame(mints_list, columns=MINTS_COLUMN_NAMES) # convert to a pandas df
  #mints_df = mints_df[mints_df['label'].notna()] # remove rows with an IRI but no label
  mints_df = get_multitab_df(MINTS_SPREADSHEET_ID, MINTS_RANGE_NAMES, MINTS_COLUMN_NAMES, startrow=1) 

  # read in TSV of terms that are already in GENEPIO
  # this TSV must have columns titled ['IRI', 'label']
  genepio_edit_df = pd.read_csv("genepio_edit_terms.tsv", sep='\t', header=0)
  genepio_edit_df['In genepio-edit.owl?'] = 'YES' # add column to be used in merge
  genepio_edit_df = genepio_edit_df.drop(columns=['type'])# drop 'type' column
  #print("genepio_edit_df")
  #print(genepio_edit_df)

  # merge mints sheet with genepio-edit sheet
  mints_review_df = pd.merge(mints_df, genepio_edit_df, on=['IRI', 'label'], how='left')
  # final df should be the same size as mints_df!

  #print(merged_df[merged_df['In genepio-edit.owl?'].notna()])

  # read in genepio-ROBOT sheet: spec_field (new)
  robot_list = get_values(GENEPIO_ROBOT_SPREADSHEET_ID, GENEPIO_ROBOT_RANGE_NAME).get("values", [])
  robot_df = pd.DataFrame(robot_list, columns=['IRI', 'label']) # convert to a pandas df
  robot_df = robot_df[robot_df['IRI'].str.contains("GENEPIO")] # remove rows with no IRI
  robot_df = robot_df[robot_df['label'].notna()] # remove rows with no label

  # check if mints are in genepio-ROBOT sheet: spec_field (new)
  robot_df['In GENEPIO ROBOT?'] = 'YES - spec field (new)' # add column to be used in merge
  robot_df['Tab location in GENEPIO ROBOT'] = 'Other ROBOT tab checks coming soon!'
  # merge mints sheet with genepio-ROBOT sheet
  mints_review_df = pd.merge(mints_review_df, robot_df, on=['IRI', 'label'], how='left')
  #print("mints_review_df")
  #print(mints_review_df)
  # final df should be the same size as mints_df!

  ### check if mints are in genepio-ROBOT archival sheets

  # print out any terms that are in the ROBOT file
  #print("terms in ROBOT spec field (new)")
  #print(merged_df_2[merged_df_2['In GENEPIO ROBOT?'].notna()])

  ## check if mints are in a curation sheet
  curation_2023_df = get_multitab_df(CURATION_SHEET_2023, CURATION_SHEET_2023_RANGE_NAMES, CURATION_SHEET_2023_COLUMN_NAMES, startrow=2)
  curation_2024_df = get_multitab_df(CURATION_SHEET_2024, CURATION_SHEET_2024_RANGE_NAMES, CURATION_SHEET_2024_COLUMN_NAMES, startrow=2)
  # concatenate curation sheets into one long df
  curation_df = pd.concat([curation_2023_df, curation_2024_df])
  # add "In GENEPIO curation?" tab
  curation_df["In GENEPIO curation?"] = 'YES'
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
  print(mints_review_df)
  print(mints_df)
  mints_review_df_values = mints_review_df.values.tolist() # convert df back to nested list
  #update_values(MINTS_SPREADSHEET_ID, "Mints review!A3:K", "RAW", mints_review_df_values)
