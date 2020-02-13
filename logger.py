import sys
from datetime import datetime

args = sys.argv[1:]
path = args[0]


def printWithTime(message):
    timestamp = datetime.now().strftime('%m/%d/%y %H:%M:%S')
    message = timestamp + ' - ' + message
    print(message)
    f = open(path + 'log.txt', 'at')
    f.write(message + '\n')
    f.close()
