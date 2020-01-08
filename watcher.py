import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import parser
from logger import printWithTime


class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.xml", "*.lxml"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there

        # To ensure the file is transferred fully before processing
        time.sleep(1)

        printWithTime(event.src_path + ' ' + event.event_type)

        # Check for PermissionError
        while True:
            try:
                f = open(event.src_path, 'rb')
                f.close()
                printWithTime('File is available')
                break
            except PermissionError:
                printWithTime('File is not available')
                time.sleep(1)

        parser.processFile(event.src_path, uniqueCheck)

    # def on_modified(self, event):
    #     self.process(event)

    # def on_moved(self, event):
    #     self.process(event)

    # def on_deleted(self, event):
    #     self.process(event)

    def on_created(self, event):
        self.process(event)


if __name__ == '__main__':
    args = sys.argv[1:]
    path = args[0]
    uniqueCheck = int(args[1])
    observer = Observer()
    observer.schedule(MyHandler(), path if args else '.')
    observer.start()
    printWithTime('Watching: ' + path)
    printWithTime('Unique FileID Check [1/0]: ' + str(uniqueCheck))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
