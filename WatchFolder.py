import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from ParseXMLtoSQL import processFile


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
        print(event.src_path, event.event_type)

        # Check for PermissionError
        while True:
            try:
                f = open(event.src_path, 'rb')
                f.close()
                print('File is available')
                break
            except PermissionError:
                print('File is not available')
                time.sleep(1)

        processFile(event.src_path)

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
    observer = Observer()
    observer.schedule(MyHandler(), path if args else '.')
    observer.start()
    print('Watching: ' + path)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
