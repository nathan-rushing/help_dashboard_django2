import pandas as pd

"""
Displays the sections from the Radiant 2025.1 help assignments dataset.
"""
df = pd.read_excel('online_help/management/dataset/Radiant_2025.1_help_assignments_v3_copy.xlsx')

subsection_column = df['Sub-sections'].dropna()
# print(subsection_column)