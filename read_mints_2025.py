import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
#SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# The ID and range of a sample spreadsheet.
#SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms" #original sample
SAMPLE_SPREADSHEET_ID = "1tcFcInsaGcrKpJKcdKGxzCpV7BvmvDQLIH2BLbnso1g" #mine
#SAMPLE_SPREADSHEET_ID = "1Ieo0jokfXBbWIQv32g5D5s7x8FIeh7f-gGX6qI6AhN0" #mints sheet
SAMPLE_RANGE_NAME = "A2:B" # use the form "Sheet!ColumnRow:ColumnRow", eg. "2025!A2:B"


def main():
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

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()

    # Try retrieving data from a spreadsheet
    result = (
        sheet.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
        .execute()
    )
    values = result.get("values", []) # this is a list of lists

    if not values:
      print("No data found.")
      return
    
    # print out the data raw
    print("type:")
    print(type(values))
    print(values)
    print("")

    # print out the data prettily
    print("ColumnA, ColumnB:")
    for row in values:
      # Print columns A and B, which correspond to indices 0 and 1.
      print(f"{row[0]}, {row[1]}")

    # now try creating an empty spreadsheet in the Root folder of my Drive
    spreadsheet = {"properties": {"title": "Madeline_26"}}
    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )
    print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
    return spreadsheet.get("spreadsheetId")

  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()
