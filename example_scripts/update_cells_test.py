#This is to test update_values().

import os.path
import pandas as pd
import numpy as np

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from functions import *

CURATION_SHEET_2023 = "1s6FB9EyPWYBgssIU9a9AKATEfZnMdixwvrGhBXUHAVk" # GENEPIO 2023 Curation Tables

# get multiple sheets within CURATION_SHEET_2023 into one large df
values = batch_get_values(CURATION_SHEET_2023, ["2023_to_request_ontologies (Charlie)", "2023_mints_wastewater (Charlie)"])
# initialize empty df
curation_2023_df = pd.DataFrame(columns=['Ontology ID','label', 'alternative label', 'tab', 'spreadsheet_id'])
for sheet in range(len(values['valueRanges'])):
    tab = values['valueRanges'][sheet]['range'].split('!')[0] # save the name of the tab, eg. '2023_error_curation (Charlie)'
    #print(tab)
    # collect the data in that tab in a pandas df
    sheet_data = values['valueRanges'][sheet]['values']
    sheet_df = pd.DataFrame(sheet_data, columns=sheet_data[0])
    sheet_df = sheet_df[2:] # leave off ROBOT instructions
    #print(sheet_df.columns)
    # only keep ['Ontology ID','label', 'alternative label'] columns
    sheet_df = sheet_df[['Ontology ID','label', 'alternative label']]
    # add a column showing the tab name
    sheet_df["tab"] = tab
    sheet_df["spreadsheet_id"] = CURATION_SHEET_2023
    #print(sheet_df)
    # append sheet_df to the spreadsheet df
    curation_2023_df = pd.concat([curation_2023_df, sheet_df])
print(curation_2023_df)


  # get multiple sheets within CURATION_SHEET_2023 into one large df
  values = batch_get_values(CURATION_SHEET_2023, ["2023_to_request_ontologies (Charlie)", "2023_mints_wastewater (Charlie)"])
  # initialize empty df
  curation_2023_df = pd.DataFrame(columns=['Ontology ID','label', 'alternative label', 'tab', 'spreadsheet_id'])
  for sheet in range(len(values['valueRanges'])):
      tab = values['valueRanges'][sheet]['range'].split('!')[0] # save the name of the tab, eg. '2023_error_curation (Charlie)'
      #print(tab)
      # collect the data in that tab in a pandas df
      sheet_data = values['valueRanges'][sheet]['values']
      sheet_df = pd.DataFrame(sheet_data, columns=sheet_data[0])
      sheet_df = sheet_df[2:] # leave off ROBOT instructions
      #print(sheet_df.columns)
      # only keep ['Ontology ID','label', 'alternative label'] columns
      sheet_df = sheet_df[['Ontology ID','label', 'alternative label']]
      # add a column showing the tab name
      sheet_df["tab"] = tab
      sheet_df["spreadsheet_id"] = CURATION_SHEET_2023
      #print(sheet_df)
      # append sheet_df to the spreadsheet df
      curation_2023_df = pd.concat([curation_2023_df, sheet_df])
  print(curation_2023_df)
  # check for duplicates in curation sheet
  print(curation_2023_df[curation_2023_df.duplicated()==True])
