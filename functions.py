import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pandas as pd


def create(title):
  """
  https://github.com/googleworkspace/python-samples/blob/main/sheets/snippets/sheets_create.py

  Creates the Sheet the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.

    # Pass: title
  create("mysheet1")
  """
  creds, _ = google.auth.default()
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)
    spreadsheet = {"properties": {"title": title}}
    spreadsheet = (
        service.spreadsheets()
        .create(body=spreadsheet, fields="spreadsheetId")
        .execute()
    )
    print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
    return spreadsheet.get("spreadsheetId")
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error
  


  
def get_values(spreadsheet_id, range_name):
  """
  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  creds, _ = google.auth.default()
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)

    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    rows = result.get("values", [])
    print(f"{len(rows)} rows retrieved")
    return result
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error

  


def update_values(spreadsheet_id, range_name, value_input_option, values, creds):
  """
  https://github.com/googleworkspace/python-samples/blob/main/sheets/snippets/sheets_update_values.py

  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.

    # Pass: spreadsheet_id,  range_name, value_input_option and  _values
  update_values(
      "1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
      "A1:C2",
      "USER_ENTERED",
      [["A", "B"], ["C", "D"]],
  )
  """
  #creds, _ = google.auth.default()
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body,
        )
        .execute()
    )
    print(f"{result.get('updatedCells')} cells updated.")
    return result
  
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error



def append_values(spreadsheet_id, range_name, value_input_option, _values):
  """
  https://github.com/googleworkspace/python-samples/blob/main/sheets/snippets/sheets_append_values.py

  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.

    # Pass: spreadsheet_id, range_name value_input_option and _values)
  append_values(
      "1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
      "A1:C2",
      "USER_ENTERED",
      [["F", "B"], ["C", "D"]],
  )
  """
  creds, _ = google.auth.default()
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)

    values = [
        [
            # Cell values ...
        ],
        # Additional rows ...
    ]
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body,
        )
        .execute()
    )
    print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
    return result

  except HttpError as error:
    print(f"An error occurred: {error}")
    return error



def batch_get_values(spreadsheet_id, range_names, creds):
  """
  https://github.com/googleworkspace/python-samples/blob/main/sheets/snippets/sheets_batch_get_values.py

  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.


  # Pass: spreadsheet_id, and range_name

  batch_get_values("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k", "A1:C2")
  """
  #creds, _ = google.auth.default()
  # pylint: disable=maybe-no-member
  try:
    service = build("sheets", "v4", credentials=creds)

    result = (
        service.spreadsheets()
        .values()
        .batchGet(spreadsheetId=spreadsheet_id, ranges=range_names)
        .execute()
    )
    ranges = result.get("valueRanges", [])
    print(f"{len(ranges)} ranges retrieved")
    return result
  except HttpError as error:
    print(f"An error occurred: {error}")
    return error


def get_multitab_df(input_dict, creds):
  # eg. range_names = ["2023_to_request_ontologies (Charlie)", "2023_mints_wastewater (Charlie)"]
  # eg. column_names = ['Ontology ID','label', 'alternative label']
  # get multiple sheets within spreadsheet_id into one large df
  # startrow is 0-indexed: so if the first row of data is row 2 in Google Sheets, write startrow=1 here
  spreadsheet_id = input_dict.pop("SPREADSHEET_ID")
  print("Processing: ", spreadsheet_id)
  range_names = input_dict.pop("RANGE_NAMES")
  column_names = input_dict.pop("COLUMN_NAMES")
  start_row = input_dict.pop("START_ROW")
  values = batch_get_values(spreadsheet_id, range_names, creds)
  # initialize empty df
  multitab_df = pd.DataFrame(columns=column_names)

  # fill in empty df sheet by sheet
  for sheet in range(len(values['valueRanges'])):
      tab = values['valueRanges'][sheet]['range'].split('!')[0] # save the name of the tab, eg. '2023_error_curation (Charlie)'
      print(tab)
      # collect the data in that tab in a pandas df
      sheet_data = values['valueRanges'][sheet]['values']
      sheet_df = pd.DataFrame(sheet_data, columns=sheet_data[0])
      sheet_df = sheet_df[start_row:] # leave off ROBOT instructions
      # replace '\n' in column names with a space
      sheet_df.columns = [colname.replace('\n', ' ') for colname in sheet_df.columns.tolist()]
      # only keep columns specified in column_names variable
      sheet_df = sheet_df[column_names]
      # add a column showing the tab name
      sheet_df["tab"] = tab
      # append sheet_df to the spreadsheet df
      multitab_df = pd.concat([multitab_df, sheet_df])
  # combine duplicate rows and transform "tab" into a comma-separated list
  sheet_df = sheet_df.fillna('')
  multitab_df = multitab_df.groupby(column_names).agg({'tab': ', '.join}).reset_index()
  # add a column showing the spreadsheet_id
  # multitab_df["spreadsheet_id"] = spreadsheet_id
  #print(multitab_df)

  return multitab_df


def compare_terms(mints_df, search_df, result_column, tab_column):

  # if both ID and label match, record 'id_and_label_match' in result_column
  # if tab_column != None, record tab name in tab_column
  search_df['id_and_label_match'] = 'id_and_label_match' # add column to be used in merge
  # if tab_column != None, record tab name in tab_column
  if tab_column != None:
    search_df['id_and_label_match_tab'] = search_df['tab']
  else:
    search_df['id_and_label_match_tab'] = ''
  merged_df = pd.merge(mints_df, search_df[['IRI', 'label', 'id_and_label_match', 'id_and_label_match_tab']], on=['IRI', 'label'], how='left')

  # elif only the ID matches, record "id_match" in result_column
  search_df['id_match'] = 'id_match' # add column to be used in merge
  # if tab_column != None, record tab name in tab_column
  if tab_column != None:
    search_df['id_match_tab'] = search_df['tab']
  else:
    search_df['id_match_tab'] = ''
  merged_df = pd.merge(merged_df, search_df[['IRI', 'id_match', 'id_match_tab']], on=['IRI'], how='left')
  
  # elif only the label matches, record "label_match" in result_column
  search_df['label_match'] = 'label_match' # add column to be used in merge
  # if tab_column != None, record tab name in tab_column
  if tab_column != None:
    search_df['label_match_tab'] = search_df['tab']
  else:
    search_df['label_match_tab'] = ''
  merged_df = pd.merge(merged_df, search_df[['label', 'label_match', 'label_match_tab']], on=['label'], how='left')

  # merge all match results into result_column
  # fill in 'no_match' as the default
  merged_df[result_column] = 'no_match'
  if tab_column != None:
    merged_df[tab_column] = ''
  # fill in 'id_and_label_match'
  id_and_label_match_mask = (merged_df['id_and_label_match'] == 'id_and_label_match')
  merged_df.loc[id_and_label_match_mask, result_column] = 'id_and_label_match'
  if tab_column != None:
    merged_df.loc[id_and_label_match_mask, tab_column] = merged_df['id_and_label_match_tab']
  # fill in 'id_match'
  id_match_mask = (merged_df['id_match'] == 'id_match') & (merged_df[result_column] == 'no_match')
  merged_df.loc[id_match_mask, result_column] = 'id_match'
  if tab_column != None:
    merged_df.loc[id_match_mask, tab_column] = merged_df['id_match_tab']
  # fill in 'label_match'
  label_match_mask = (merged_df['label_match'] == 'label_match') & (merged_df[result_column] == 'no_match')
  merged_df.loc[label_match_mask, result_column] = 'label_match'
  if tab_column != None:
    merged_df.loc[label_match_mask, tab_column] = merged_df['label_match_tab']
  # fill in 'id_and_label_cross_row_match'
  id_and_label_cross_row_match_mask = (merged_df['label_match'] == 'label_match') & (merged_df['id_match'] == 'id_match') & (merged_df['id_and_label_match'] != 'id_and_label_match')
  merged_df.loc[id_and_label_cross_row_match_mask, result_column] = 'id_and_label_cross_row_match'
  if tab_column != None:
    merged_df.loc[id_and_label_cross_row_match_mask, tab_column] = 'ID in ' + merged_df['id_match_tab'] + '; label in ' + merged_df['label_match_tab']
  # restrict columns to original mints_df columns + result_column + tab_column
  merged_df = merged_df.drop(columns=['id_and_label_match', 'id_and_label_match_tab', 'id_match', 'id_match_tab', 'label_match', 'label_match_tab'])

  return merged_df
