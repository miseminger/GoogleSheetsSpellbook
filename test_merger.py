# https://www.geeksforgeeks.org/python/python-grouping-similar-substrings-in-list/
# 
# Python3 code to demonstrate
# group similar substrings
# using lambda + itertools.groupby() + split()
from itertools import groupby
import pandas as pd
from functions import get_hyperlinks_list, get_hyperlinks_df

# initializing list 
test_list = ['geek_1', 'coder_2', 'geek_4', 'coder_3', 'pro_3']
print(test_list)

test = get_hyperlinks_list(test_list)
print("testing")
print(test)


hyperlink_column_prefix = 'curation_sheet'
df = pd.DataFrame(data={'a':["geek_1,geek_2", "", "coder_3,geek_4", "pro_3,coder_2,coder_3,geek_17","geek_1"], 'b':[0,31,1,29,999]})
print(df)
tab_column = 'a'

z = get_hyperlinks_df(df, tab_column, hyperlink_column_prefix)
print(z)
print(z.columns)