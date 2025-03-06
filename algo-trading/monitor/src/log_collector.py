import os
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogCollector:
    def __init__(self):
        with open('config/logging_config.yml', 'r') as f:
            self.config = yaml.safe_load(f)
        self.log_dir = self.config['log_dir']
        self.setup_watchers()

    def setup_watchers(self):
        self.observer = Observer()
        for container in self.config['containers']:
            log_path = os.path.join(self.log_dir, container['log_file'])
            self.observer.schedule(LogHandler(container['name']), path=log_path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

class LogHandler(FileSystemEventHandler):
    def __init__(self, container_name):
        self.container_name = container_name

    def on_modified(self, event):
        if not event.is_directory:
            self.process_log(event.src_path)

    def process_log(self, log_path):
        # Here you would implement log processing logic
        # For example, parsing the log, storing in database, etc.
        print(f"Processing log for {self.container_name}: {log_path}")