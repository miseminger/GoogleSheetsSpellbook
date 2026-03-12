import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import groupby

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
  


  
def get_values(spreadsheet_id, range_name, creds):
  """
  Creates the batch_update the user has access to.
  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """
  #creds, _ = google.auth.default()
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
  

def get_multitab_df(input_dict, creds):
  # eg. range_names = ["2023_to_request_ontologies (Charlie)", "2023_mints_wastewater (Charlie)"]
  # eg. column_names = ['Ontology ID','label', 'alternative label']
  # get multiple sheets within spreadsheet_id into one large df
  # startrow is 0-indexed: so if the first row of data is row 2 in Google Sheets, write startrow=1 here
  spreadsheet_id = input_dict.pop("SPREADSHEET_ID")
  print("Processing: ", spreadsheet_id)
  range_names = input_dict.pop("RANGE_NAMES")
  column_names = input_dict.pop("COLUMN_NAMES")
  #print(column_names)
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
      print("    " + tab)
      # collect the data in that tab in a pandas df
      sheet_data = values['valueRanges'][sheet]['values']
      sheet_df = pd.DataFrame(sheet_data, columns=sheet_data[0])
      sheet_df = sheet_df[start_row:] # leave off ROBOT instructions
      # replace '\n' in column names with a space
      sheet_df.columns = [colname.replace('\n', ' ') for colname in sheet_df.columns.tolist()]
      # only keep columns specified in column_names variable
      sheet_df = sheet_df[column_names]
      # add a column showing the spreadsheet_id and tab name in readiness for adding hyperlinks later
      sheet_df["tab"] = spreadsheet_id + ':' + tab 
      # append sheet_df to the spreadsheet df
      multitab_df = pd.concat([multitab_df, sheet_df])
  multitab_df = multitab_df.fillna('')
  # combine duplicate rows and transform "tab" into a comma-separated list
  multitab_df = multitab_df.groupby(column_names).agg({'tab': ','.join}).reset_index()
  # rename columns according to rename_columns attribute
  multitab_df = multitab_df.rename(columns=rename_columns)

  return multitab_df


def compare_terms(mints_df, search_df, result_column, tab_column):

  # save the label in its original format to have at the end
  mints_df['search_label'] = mints_df['label']
  search_df = search_df.rename(columns={'label': 'search_label'})

  if tab_column != None:
    search_df = search_df.rename(columns={'tab': tab_column})

  # make 'search_label' columns of mints_df and search_df lowercase
  mints_df['search_label'] = mints_df['search_label'].str.lower()
  search_df['search_label'] = search_df['search_label'].str.lower()
  # make spaces and underscores equivalent for search
  mints_df['search_label'] = mints_df['search_label'].str.replace(' ', '_', regex=False)
  search_df['search_label'] = search_df['search_label'].str.replace(' ', '_', regex=False)

  # if the search_df doesn't already include an 'alternative label' column, add an empty one
  #print("search_df.columns")
  #print(search_df.columns)
  if 'alternative label' not in search_df.columns:
    search_df['alternative label'] = ''
  # get a set of all the alternative labels in search_df
  #alternative_labels_list = search_df['alternative label'].unique().tolist()
  #alternative_labels_list = [x for x in alternative_labels_list if type(x)==str]
  #alternative_labels_list = [x.replace('\n', '|') for x in alternative_labels_list]
  #print(alternative_labels_list)

  id_merge = pd.merge(mints_df[["IRI", "search_label"]], search_df, on='IRI', how='inner')
  id_merge[result_column] = 'id_match'
  id_and_label_match_mask = (id_merge['search_label_x'] == id_merge['search_label_y']) 
  id_merge.loc[id_and_label_match_mask, result_column] = 'id_and_label_match'
  # drop label_y
  id_merge = id_merge.drop(columns=['search_label_y'])
  # drop duplicates
  id_merge = id_merge.drop_duplicates(keep='first')
  # groupby match type, making tabs into a list
  if tab_column != None:
      groupby_columns = id_merge.columns.tolist() 
      groupby_columns.remove(tab_column)
      id_merge = id_merge.groupby(by=groupby_columns).agg({tab_column: ','.join}).reset_index()
  id_merge = id_merge.rename(columns={'search_label_x': 'search_label'})

  label_merge = pd.merge(mints_df[["IRI", "search_label"]], search_df, on='search_label', how='inner')
  # record 'label_match' where IRI_x and IRI_y are different
  label_merge[result_column] = ''
  label_match_mask = (label_merge['IRI_x'] != label_merge['IRI_y']) 
  label_merge.loc[label_match_mask, result_column] = 'label_match'
  # only keep rows that contain 'label_match'
  label_merge = label_merge[label_merge[result_column]=='label_match']
  # drop IRI_y
  label_merge = label_merge.drop(columns=['IRI_y'])
  # drop duplicates
  label_merge = label_merge.drop_duplicates(keep='first')
  # groupby match type, making tabs into a list
  if tab_column != None:
      groupby_columns = label_merge.columns.tolist() 
      groupby_columns.remove(tab_column)
      label_merge = label_merge.groupby(by=groupby_columns).agg({tab_column: ','.join}).reset_index()
  # rename IRI_x to IRI
  label_merge = label_merge.rename(columns={'IRI_x': 'IRI'})

  # concatenate id_merge and label_merge
  match_df = pd.concat([id_merge, label_merge])
  # merge into mints_df
  merged_df = pd.merge(mints_df, match_df, how='left', on=['IRI', 'search_label'])
  merged_df[result_column] = merged_df[result_column].fillna('no_match')
  merged_df = merged_df.fillna('')
  
  return merged_df


def count_matches_by_subset(df, owl_column, robot_column, curation_column):

  no_match_mask = (df[owl_column]=='no_match') & (df[robot_column]=='no_match') & (df[curation_column]=='no_match')

  # count how many terms in each subset have no match anywhere
  no_match_df = df[no_match_mask]
  no_match_counts = no_match_df['subset'].value_counts().rename_axis('Subset').reset_index(name='no_match_counts')

  # count how many terms in each subset have at least one ID or Label match somewhere
  min_1_match_df = df[~no_match_mask]
  min_1_match_df = min_1_match_df.drop_duplicates(subset=["IRI"])
  min_1_match_counts = min_1_match_df['subset'].value_counts().rename_axis('Subset').reset_index(name='min_1_match_counts')

  # merge into one df
  match_counts_df = pd.merge(no_match_counts, min_1_match_counts, on='Subset', how='outer')
  match_counts_df.loc[match_counts_df['Subset']=='', 'Subset'] = 'No subset given'
  match_counts_df = match_counts_df.fillna(0)
  match_counts_df['no_match_counts'] = match_counts_df['no_match_counts'].astype(int)
  match_counts_df['min_1_match_counts'] = match_counts_df['min_1_match_counts'].astype(int)
  match_counts_df = match_counts_df.set_index('Subset')
  print(match_counts_df)

  return match_counts_df


def get_hyperlinks_list(tabs_list):
    
    # from a list of spreadsheet ids and tab names, return a list of hyperlinks (one per sheet id)
    # example input: ['coder_2', 'coder_3', 'geek_1', 'geek_4', 'pro_3']
    # example output: =HYPERLINK('coder', '2, 3'),=HYPERLINK('geek', '1, 4'),=HYPERLINK('pro', '3')
    
    # sort list: essential for grouping
    tabs_list.sort()
    # get list of unique spreadsheet ids
    ids = [j for j, i in groupby(tabs_list,
                  lambda a: a.split(':')[0])]
    # group tabs_list into sublists by spreadsheet id
    grouped_tabs = [list(i) for j, i in groupby(tabs_list,
                  lambda a: a.split(':')[0])]
    # transform nested grouped_tabs_list into a nested list of suffixes
    for i in range(len(grouped_tabs)):
        for j in range(len(grouped_tabs[i])):
            grouped_tabs[i][j] = grouped_tabs[i][j].split(':')[1]
    # return "=HYPERLINK('prefix', 'suffix_a, suffix_b, ..., suffix_n')"
    link_list = []
    for i in range(len(ids)):
        link_list.append('=HYPERLINK("https://docs.google.com/spreadsheets/d/' + ids[i] + '", "' + ', '.join(grouped_tabs[i]) + '")')
    hyperlinks = (';'.join(link_list))
    
    return hyperlinks


def get_hyperlinks_df(df, tab_column):
# Given a df with a column containing comma-separated strings of the form '"spreadsheet_id":"tab",spreadsheet_id_tab,...,n',
#  return the same df with clickable columns of hyperlinks (one column per spreadsheet_id),
#  where the column names are 'tab_column_1', 'tab_column_2', etc.
# 
# The parameters are:
# df: a Pandas df containing the id_tab string type shown above
# tab_column: the column name in the df to extract hyperlinks from
# tab_column: for the new hyperlinks columns to which will be appended underscores and integers
 
    # make sure the column doesn't contain NaNs, only empty strings
    df[tab_column] = df[tab_column].fillna('')
    # fetch df column into nested list: one list per row
    column_list = df[tab_column].values.tolist()
    # separate the single string in each list into many strings, splitting at commas
    column_list = [x.split(',') for x in column_list]
    # go through the column row-by-row and add hyperlinks
    for sublist in range(len(column_list)):
        # if a row is just an empty string, return it as-is without adding a hyperlink
        if len(column_list[sublist])==1 and column_list[sublist][0]=='':
            column_list[sublist] = column_list[sublist]
        # if a row is not empty, add hyperlinks separated by ';'
        else:
            column_list[sublist] = get_hyperlinks_list(column_list[sublist])
    # add these hyperlinks to the df in a new column called 'hyperlinks'
    df['hyperlinks'] = column_list
    # split the 'hyperlinks' column into several columns, splitting at each ';'
    hyperlinks_df = df['hyperlinks'].str.split(";", expand=True)
    # replace NaNs and Nones with ''
    hyperlinks_df = hyperlinks_df.fillna('')
    # rename the columns to "tab_column" + integer beginning at 1 (no integer if there is only one column)
    if hyperlinks_df.shape[1]==1:
      hyperlinks_df_cols = [tab_column]
    else:
      hyperlinks_df_cols = [tab_column + '_' + str(x) for x in list(range(1, hyperlinks_df.shape[1] + 1))]
    hyperlinks_df.columns = hyperlinks_df_cols
    # delete all single quotes from df
    for column in hyperlinks_df.columns:
      hyperlinks_df[column] = hyperlinks_df[column].str.replace("'", "")
    # drop original column so its label doesn't get duplicated during concatenation
    df = df.drop(columns=[tab_column])
    # add the separated and renamed hyperlinks columns to the original df
    full_df = pd.concat((df, hyperlinks_df), axis=1)
    full_df = full_df.drop(columns=['hyperlinks'])        
    # return the df with added columns
    return(full_df)



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
