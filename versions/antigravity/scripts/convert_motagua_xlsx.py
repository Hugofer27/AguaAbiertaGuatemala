import zipfile
import xml.etree.ElementTree as ET
import csv
import os

xlsx_path = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/raw/ngos_cleanup/TheOceanCleanup_Motagua_Field_Data_2019.xlsx"
out_csv = "D:/Documentos D/BaseDatosGT H2O/Investigación Antigravity/data/processed/TheOceanCleanup_Motagua_Morales_2019_Flux.csv"

z = zipfile.ZipFile(xlsx_path)

# 1. Parse shared strings
strings = []
if 'xl/sharedStrings.xml' in z.namelist():
    tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
        # join all text elements
        t_parts = [t.text for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text]
        strings.append("".join(t_parts))

# 2. Parse sheet1.xml
tree = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

rows_data = []
for row in tree.findall(f'{ns}sheetData/{ns}row'):
    row_num = row.get('r')
    row_cells = {}
    for c in row.findall(f'{ns}c'):
        ref = c.get('r') # e.g. A1, B2
        # extract col letters
        col_letters = ''.join([ch for ch in ref if ch.isalpha()])
        c_type = c.get('t')
        v_elem = c.find(f'{ns}v')
        val = ""
        if v_elem is not None and v_elem.text is not None:
            raw_v = v_elem.text
            if c_type == 's':
                val = strings[int(raw_v)] if int(raw_v) < len(strings) else raw_v
            else:
                val = raw_v
        row_cells[col_letters] = val
    rows_data.append(row_cells)

# Determine all columns
all_cols = sorted(list(set([col for r in rows_data for col in r.keys()])))

# Write raw parsed rows
with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for r in rows_data:
        writer.writerow([r.get(c, "") for c in all_cols])

print(f"Extracted {len(rows_data)} rows from Excel XML to {out_csv}")
# Print non-empty rows
for i, r in enumerate(rows_data):
    non_empty = {k: v for k, v in r.items() if v.strip()}
    if non_empty:
        print(f"Row {i+1}: {non_empty}")
