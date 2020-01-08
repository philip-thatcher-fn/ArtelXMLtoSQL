from datetime import datetime

def printWithTime(message):
    timestamp = datetime.now().strftime('%m/%d/%y %H:%M:%S')
    print(timestamp + ' - ' + message)