import pandas as pd
from online_help.management.utility.split_comment import split_comments

# Load your Excel file
df = pd.read_excel('online_help/management/dataset/Radiant_2025.1_help_assignments_v3_copy.xlsx', sheet_name='radiant_docu')

section_data_radiant_docu = df['Radiant Documentation'].dropna().tolist()  # Only get the column as a list
