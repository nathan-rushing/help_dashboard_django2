import pandas as pd
from online_help.management.utility.split_comment import split_comments

"""
Displays the sections from the Radiant 2025.1 help assignments dataset.
"""
# section_column = df['Section'].dropna()
# print(section_column)


# Load your Excel file
df = pd.read_excel('online_help/management/dataset/Radiant_2025.1_help_assignments_v3_copy.xlsx', sheet_name='pdf_documents')

# Drop rows where any necessary column is missing
# df = df.dropna(subset=['Section', 'Sub-sections', 'color', 'Writer'])

# Group by Section and collect Sub-section, Color, Writer, and split Comments
grouped = df.groupby('Section', sort=False).apply(
    lambda x: [
        (row['Sub-sections'], row['color'], row['Writer'], split_comments(row['Comments']))
        for _, row in x.iterrows()
    ]
).reset_index(name='subsections')

# Convert to list of dicts for the template
section_data_pdf = grouped.to_dict(orient='records')

# # Group by Section, and collect Sub-section + Color as tuples
# grouped = df.groupby('Section').apply(
#     lambda x: list(zip(x['Sub-sections'], x['color']))
# ).reset_index(name='Subsection_Color_Pairs')

# Display results
# for _, row in grouped.iterrows():
#     print(f"Section: {row['Section']}")
#     print("Sub-sections and Colors:")
#     for sub, color in row['Subsection_Color_Pairs']:
#         print(f" - {sub} (Color: {color})")
#     print()


# print(section_data)
# print(grouped['Section'])
# print(grouped)