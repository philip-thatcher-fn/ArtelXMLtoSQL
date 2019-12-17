# This script processes Artel Data Manager XML files and pushes relevant data to a MySQL Database
import xmltodict


# Opening file to read with binary encoding and parsing to dict
def parseXML(path):
    with open(path, 'rb') as f:
        doc = xmltodict.parse(f.read())
    return doc


# doc = parseXML('3uL 1_10.xml')
doc = parseXML('3_10uL_CHi.xml')

# Store header info
header = doc['Data']['Header3']
print('Header:')
print(header)

# Determine file type
# Create 'groups' (a list) with each group dict as a separate element
groups = []
try:
    # Full Plate Format Test
    groupsTmp = doc['Data']['Plate']
except KeyError:
    # Partial Plate (Group) Format
    print('Parsing in Partial Plate (Group) mode...')
    mode = 'group'
    for x in doc['Data']['Group']:
        groups.append(x)
else:
    # Full Plate Format
    print('Parsing in Full Plate mode...')
    mode = 'plate'
    groupsTmp = doc['Data']['Plate']
    groups.append(groupsTmp)

# Examine groupsLst
groupsLen = len(groups)
print('groups Length: ' + str(groupsLen))
print('Groups:')
print(groups)

if mode == 'plate':
    target = doc['Data']['Run_Statistics']['Target_Volume']

# Loop through groupsLst to pull out relevant info
for i in range(groupsLen):
    # Write group dict from the group list
    group = groups[i]

    # get statistics if mode = group
    if mode == 'group':
        target = group['Group_Run_Statistics']['Target_Volume']

    # Get volume data
    rows = group['Well_Volumes']['Rows']
    rowsLen = len(rows)
    columnsLen = len(rows[1]['Column'])
    print('Rows: ' + str(rowsLen))
    print('Column: ' + str(columnsLen))

    values = []  # A1, A2, A3 ... B1 ...
    # Looping through rows
    for x in range(rowsLen):
        # print(rows[x]['Column'])
        # Looping through 'Column' to get 'Value'
        for y in range(columnsLen):
            value = rows[x]['Column'][y]['Value']
            values.append(value)

    print('Target Volume:')
    print(target)
    print('Values:')
    print(values)
