import sys
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from xml_parser import processFile

from util import log
from util import getPath

args = sys.argv[1:]
uniqueCheck = int(args[1])

path = getPath()


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

        log(event.src_path + ' ' + event.event_type)

        # Check for PermissionError
        while True:
            try:
                f = open(event.src_path, 'rb')
                f.close()
                log('File is available')
                break
            except PermissionError:
                log('File is not available')
                time.sleep(1)

        processFile(event.src_path, uniqueCheck)

    # def on_modified(self, event):
    #     self.process(event)

    # def on_moved(self, event):
    #     self.process(event)

    # def on_deleted(self, event):
    #     self.process(event)

    def on_created(self, event):
        self.process(event)


if __name__ == '__main__':
    observer = Observer()
    observer.schedule(MyHandler(), path if args else '.')
    observer.start()
    log('Watching: ' + path)
    log('Unique FileID Check [1/0]: ' + str(uniqueCheck))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
