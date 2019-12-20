# This script processes Artel Data Manager XML files and pushes relevant data to a MySQL Database
import xmltodict
import mysql.connector
from dateutil.parser import parse
import time


# Opening file to read with binary encoding and parsing to dict
def xmlToDict(path):
    with open(path, 'rb') as f:
        doc = xmltodict.parse(f.read())
    return doc

# Reformats FileID to get time in format: YYMMDDSSHHMISS
def getTime(data):
    header = data['Header3']
    time = f"{header['Date']} {header['Time']}"
    return parse(time)

def getWellData(doc):
    data = doc['Data']

    outputData = {}

    # Create Unique ID and save to output dict
    sn = data['Plate_Reader']['Serial_Number']
    breakpoint()
    dateTime = getTime(data)
    # uid = dateTime + '_' + sn + '_welldata'
    # outputData['UniqueID'] = uid

    # Create Col Names and save to output dict
    outputData['ColNames'] = ['row', 'column', 'actual_vol']


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
        groupData = []

        # remove spaces from group name
        groupNameTmp = group['Name'].replace(' ', '')
        groupName = groupNameTmp.lower()

        # Push group name to lst
        groupNames.append(groupName)

        # get target volume if mode = 'group'
        if mode == 'group':
            target = group['Group_Run_Statistics']['Target_Volume']

        rows = group['Well_Volumes']['Rows']

        colNames = [x['Name'] for x in group['Well_Volumes']['Columns']['Column']]

        for row in rows:
            rowName = row['Row']
            for (well, colName) in zip(row['Column'], colNames):
                groupData.append([rowName, colName, well['Value']])

        # print(groupData)

        outputData[groupName] = groupData
    outputData['Groups'] = groupNames
    return outputData


def getRunData(doc):
    data = doc['Data']

    outputData = {}


def xmlToData(path):
    # Parsed XML file dict
    data = xmlToDict(path)
    # Extract well data
    wellData = getWellData(data)
    print(wellData)
    return wellData


# Input dictionary must have the following keys:
def dataToDB(data, dbName):
    db = mysql.connector.connect(host='localhost',
                                 user='python_user',
                                 passwd='*f39SEXJlUG1',
                                 database=dbName
                                 )
    cursor = db.cursor()

    for i in range(len(data['Groups'])):
        # Create Table and Populate Table Commands
        tableName = data['UniqueID'] + '_' + data['Groups'][i]

        cmdCreateTable = 'CREATE TABLE ' + tableName + ' (id INT AUTO_INCREMENT PRIMARY KEY, '
        cmdPopulateTable = 'INSERT INTO ' + tableName + ' ('
        for x in data['ColNames']:
            if x != data['ColNames'][-1]:
                cmdCreateTable += x + ' VARCHAR(255), '
                cmdPopulateTable += x + ', '
            else:
                cmdCreateTable += x + ' VARCHAR(255))'
                cmdPopulateTable += x + ') VALUES ('

                # Complete cmdPopulateTable
                for y in data['ColNames']:
                    if y != data['ColNames'][-1]:
                        cmdPopulateTable += '%s, '
                    else:
                        cmdPopulateTable += '%s)'

        #Create Table
        cursor.execute(cmdCreateTable)
        print('Table ' + tableName + ' was created.')

        # Populate Table
        currValueKey = data['Groups'][i]
        values = data[currValueKey]
        cursor.executemany(cmdPopulateTable, values)
        db.commit()
        print(str(cursor.rowcount) + " row(s) were inserted.")


pathC96 = '3uL 1_10.xml'
pathCHi = '3_10uL_CHi.xml'

data = xmlToData(pathCHi)

# dataToDB(data, 'artel_data_test')
