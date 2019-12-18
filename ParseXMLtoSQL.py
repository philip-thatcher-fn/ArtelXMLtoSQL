# This script processes Artel Data Manager XML files and pushes relevant data to a MySQL Database
import xmltodict


# Opening file to read with binary encoding and parsing to dict
def parseXML(path):
    with open(path, 'rb') as f:
        doc = xmltodict.parse(f.read())
    return doc


# doc = parseXML('3uL 1_10.xml')
doc = parseXML('3_10uL_CHi.xml')
data = doc['Data']

# Store header info
header = data['Header3']
print('Header:')
print(header)

# Determine file type
# Create 'groups' (a list) with each group dict as a separate element
# Try to use case statements or conditionals. Test if plate is present and then if group is present
groups = None
if 'Plate' in data:
    # Full Plate Format
    print('Parsing in Full Plate mode...')
    mode = 'plate'
    # groupsTmp = data['Plate']
    # groups.append(groupsTmp)
    groups = [data['Plate']]
elif 'Group' in data:
    # Partial Plate (Group) Format
    print('Parsing in Partial Plate (Group) mode...')
    mode = 'group'
    # breakpoint()
    groups = data['Group']
else:
    print('File Format Error')

# Examine groupsLst
print(f'groups Length: {len(groups)}')
print('Groups:')
print([x['Name'] for x in groups])
# print([x['Name'] for x in groups if x['Name'] == 'Mom'])

# breakpoint()

if mode == 'plate':
    target = data['Run_Statistics']['Target_Volume']

# Loop through groupsLst to pull out relevant info
# for i in range(groupsLen):
dataOut = {}
for group in groups:
    # Write group dict from the group list
    # group = groups[i]

    groupName = group['Name']

    # get statistics if mode = group
    if mode == 'group':
        target = group['Group_Run_Statistics']['Target_Volume']

    # Get volume data
    rows = group['Well_Volumes']['Rows']
    # rowsLen = len(rows)
    # columnsLen = len(rows[1]['Column'])
    # print('Rows: ' + str(rowsLen))
    # print('Column: ' + str(columnsLen))

    valuesOut = None  # [[Rows (Alpha)], [Cols (Numeric)], [Values]]
    rowsOut = []
    colsOut = []
    volOut = []
    # Looping through rows
    # breakpoint()
    colNames = [x['Name'] for x in group['Well_Volumes']['Columns']['Column']]
    # row_names = [x['Row'] for x in rows]
    # print(colNames)
    for row in rows:
        # print(rows[x]['Column'])
        # Looping through 'Column' to get 'Value'
        # for col in row['Column']:
        #     values.append(col['Value'])
        # values.append([x['Value'] for x in row['Column']])
        # breakpoint()
        rowName = row['Row']
        # print(row_name)
        # breakpoint()
        # print(rows.index(row))
        # col_name = col_names[rows.index(row['Column']['Value'])]
        for (well, colName) in zip(row['Column'], colNames):
            # print(rowName, colName, well['Value'])
            rowsOut.append(rowName)
            colsOut.append(colName)
            volOut.append(well['Value'])
    valuesOut = [rowsOut, colsOut, volOut]
    # breakpoint()
    print(valuesOut)
    dataOut[groupName] = valuesOut

print(dataOut)