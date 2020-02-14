import sys
from datetime import datetime


# Gets the file path from the input argument
def getPath():
    os = sys.platform
    args = sys.argv[1:]

    # Add trailing slash to path if needed
    path = args[0]
    if os == 'Windows':
        if path[-1] != '\\':
            path += '\\'
    elif os == 'darwin':
        if path[-1] != '/':
            path += '/'

    return path


# Returns the system OS
def getOS():
    os = sys.platform
    return os


# Prints and logs the input message with timestamp
def log(message):
    path = getPath()
    timestamp = datetime.now().strftime('%m/%d/%y %H:%M:%S')
    message = timestamp + ' - ' + message
    print(message)

    # Write to log.txt
    f = open(path + 'log.txt', 'at')
    f.write(message + '\n')
    f.close()
