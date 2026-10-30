#!/usr/bin/env python3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.ingestion.intake import IntakeProcessor

class SamplesEventHandler(FileSystemEventHandler):
    def __init__(self, processor): self.processor = processor
    def on_created(self, e):
        if not e.is_directory: self.processor.process_file(e.src_path,"created")
    def on_modified(self, e):
        if not e.is_directory: self.processor.process_file(e.src_path,"modified")

class FileWatcher:
    def __init__(self, watch_dir, callback):
        self.observer = Observer()
        self.handler = SamplesEventHandler(IntakeProcessor(callback))
        self.observer.schedule(self.handler, watch_dir, recursive=True)
    def start(self): self.observer.start()
    def stop(self): self.observer.stop(); self.observer.join()
