# This script processes Artel Data Manager XML files and pushes relevant data to a MySQL Database
import xmltodict
import mysql.connector


# Opening file to read with binary encoding and parsing to dict
def xmlToDict(path):
    with open(path, 'rb') as f:
        doc = xmltodict.parse(f.read())
    return doc


def getWellData(doc):
    data = doc['Data']

    outputData = {}

    # Create Unique ID
    sn = data['Plate_Reader']['Serial_Number']
    fileID = data['FileID']
    uid = fileID + '_' + sn + '_welldata'
    outputData['UniqueID'] = uid

    # Store header info
    # header = data['Header3']
    # print('Header:')
    # print(header)

    # Determine file type based on presence of 'Plate' key
    # Create 'groups' (a list) with each group dict as a separate element
    groups = None
    if 'Plate' in data:
        # Full Plate Format
        print('Parsing in Full Plate mode...')
        mode = 'plate'
        groups = [data['Plate']]
    elif 'Group' in data:
        # Partial Plate (Group) Format
        print('Parsing in Partial Plate (Group) mode...')
        mode = 'group'
        groups = data['Group']
    else:
        print('File Format Error!')

    # Examine groupsLst
    # print(f'groups Length: {len(groups)}')
    # print('Groups:')
    # # print([x['Name'] for x in groups if x['Name'] == 'Mom'])

    if mode == 'plate':
        target = data['Run_Statistics']['Target_Volume']

    # Loop through groups to pull out relevant info
    groupNames = []
    for group in groups:
        # remove spaces from group name
        groupNameTmp = group['Name'].replace(' ', '')
        groupName = groupNameTmp.lower()

        # Push group name to lst
        groupNames.append(groupName)

        # valuesOut = None  # [[Rows (Alpha)], [Cols (Numeric)], [Values]]
        # rowsOut = []
        # colsOut = []
        # volOut = []
        groupData = []

        # get target volume if mode = 'group'
        if mode == 'group':
            target = group['Group_Run_Statistics']['Target_Volume']

        rows = group['Well_Volumes']['Rows']

        colNames = [x['Name'] for x in group['Well_Volumes']['Columns']['Column']]

        for row in rows:
            rowName = row['Row']
            for (well, colName) in zip(row['Column'], colNames):
                # rowsOut.append(rowName)
                # colsOut.append(colName)
                # volOut.append(well['Value'])
                groupData.append([rowName, colName, well['Value']])

        # print(groupData)

        outputData[groupName] = groupData
    outputData['Groups'] = groupNames
    return outputData


def xmlToData(path):
    # Parsed XML file dict
    data = xmlToDict(path)
    # Extract well data
    wellData = getWellData(data)
    print(wellData)
    return wellData


def dataToDB(data, dbName):
    db = mysql.connector.connect(host='localhost',
                                 user='python_user',
                                 passwd='*f39SEXJlUG1',
                                 database=dbName
                                 )
    cursor = db.cursor()

    for i in range(len(data['Groups'])):
        # Create Table
        tableName = data['UniqueID'] + '_' + data['Groups'][i]
        col1 = '_row'
        col2 = '_col'
        col3 = '_vol'
        cmd = 'CREATE TABLE ' + tableName + ' (id INT AUTO_INCREMENT PRIMARY KEY, ' + col1 + ' VARCHAR(255), ' + col2 + ' VARCHAR(255), ' + col3 + ' VARCHAR(255))'
        cursor.execute(cmd)
        print('Table ' + tableName + ' was created.')

        # Populate Table
        cmd = 'INSERT INTO ' + tableName + ' (' + col1 + ', ' + col2 + ', ' + col3 + ') VALUES (%s, %s, %s)'
        currValueKey = data['Groups'][i]
        values = data[currValueKey]
        cursor.executemany(cmd, values)
        db.commit()
        print(str(cursor.rowcount) + " row(s) were inserted.")


pathC96 = '3uL 1_10.xml'
pathCHi = '3_10uL_CHi.xml'

data = xmlToData(pathC96)

dataToDB(data, 'artel_data_test')
