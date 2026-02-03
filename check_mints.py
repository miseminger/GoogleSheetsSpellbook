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
SAMPLE_RANGE_NAME = "2025!A3:B" # fetch 'IRI' and 'Label' columns from the 2025 sheet

# The absolute filepath of genepio-edit
GENEPIO_EDIT = "/home/madeline/Desktop/git_temp/genepio/src/ontology/genepio-edit.owl"

if __name__ == "__main__":

  # read 2025 mints sheet into a df
  mints_list = get_values(MINTS_SPREADSHEET_ID, SAMPLE_RANGE_NAME).get("values", [])
  mints_df = pd.DataFrame(mints_list, columns=['IRI', 'Label'])
  print(mints_df)

  '''
  In genepio-edit.owl, the terms that have been ontologized are written in like this:
    # Class: obo:GENEPIO_0000047 (secondary enzyme (LMACI))
  '''