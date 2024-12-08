import time
import logging
import threading
from collections import deque
import inspect

class CommandScheduler:
    def __init__(self, name="command", logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.run = False
        self.name = name
        self.queue_lock = threading.Lock()  # Lock to protect the queue
        self.condition = threading.Condition(self.queue_lock)  # Condition variable
        self.thread = threading.Thread(target=self._executeCommands)
        self.thread.daemon = True  # Ensure thread exits when the main program does
        self.resetQueue()

    def push(self, command):
        caller = inspect.stack()[1]
        caller_filename = caller.filename
        # print(f"Push called from file: {caller_filename}")
        
        with self.condition:  # Acquiring the condition's lock
            self.queue.append(command)
            self.condition.notify()  # Wake up the thread to process commands

    def start(self):
        if not self.thread.is_alive():
            self.run = True
            self.thread.start()

    def stop(self):
        with self.condition:
            self.run = False
            self.condition.notify_all()  # Wake up the thread to allow it to exit
        self.thread.join()  # Wait for the thread to finish

    def resetQueue(self):
        with self.queue_lock:
            self.queue = deque(maxlen=25)

    def _executeCommands(self):
        self.logger.info("[Scheduler] Scheduler started\n")
        while self.run:
            with self.condition:
                while not self.queue and self.run:
                    self.condition.wait()  # Wait until there are commands or stop is called
                if not self.run and not self.queue:
                    break  # Exit the loop if stopped and no more commands
                
                command = self.queue.popleft()  # Dequeue command

            try:
                command.run()
                time.sleep(0.005)
            except Exception as e:
                self.logger.error(f"Error executing command: {e}")

        self.resetQueue()
        self.logger.info("[Scheduler] Scheduler stopped\n")
