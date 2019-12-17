import xmltodict

# Opening file to read with binary encoding and parsing to dict
def parseXML(path):
    with open(path, 'rb') as f:
        doc = xmltodict.parse(f.read())
    return doc

# doc = parseXML('3uL 1_10.xml')
doc = parseXML('3_10uL_CHi.xml')

# Determine file type
# Create groupsDict with each group
# Create groupsLst with each group dict in a separate element
groupsLst = []
try:
    # Full Plate Format
    groupsDict = doc['Data']['Plate']
except KeyError:
    # Partial Plate (Group) Format
    print('Parsing in Partial Plate (Group) mode...')
    mode = 'group'
    groupsDict = doc['Data']['Group']
    for x in groupsDict:
        groupsLst.append(x)
else:
    # Full Plate Format
    print('Parsing in Full Plate mode...')
    mode = 'plate'
    # rows = doc['Data']['Plate']['Well_Volumes']['Rows']
    groupsDict = doc['Data']['Plate']
    groupsLst.append(groupsDict)

# Examine groupsLst
groupsLstLen = len(groupsLst)
print('groupLst Length: ' + str(groupsLstLen))
print(groupsLst)

# Loop through groupsLst to pull out info
for i in range(groupsLstLen):
    group = groupsLst[i]
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

    print(values)