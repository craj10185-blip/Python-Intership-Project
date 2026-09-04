import sys
import sqlite3
import os

class PyChronicleTracer:
    def __init__(self, db_name="chronicle.db"):
        if os.path.exists(db_name):
            os.remove(db_name)
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS execution_log (
                step INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                line_no INTEGER,
                event TEXT,
                variables TEXT
            )
        ''')
        self.conn.commit()
        self.step_count = 0

    def trace_calls(self, frame, event, arg):
        if event == 'call':
            return self.trace_lines
        return None

    def trace_lines(self, frame, event, arg):
        if event == 'line':
            self.step_count += 1
            filename = os.path.basename(frame.f_code.co_filename)
            line_no = frame.f_lineno
            variables = str(frame.f_locals)
            
            self.cursor.execute(
                "INSERT INTO execution_log (filename, line_no, event, variables) VALUES (?, ?, ?, ?)",
                (filename, line_no, event, variables)
            )
            self.conn.commit()
        return self.trace_lines

    def start(self):
        sys.settrace(self.trace_calls)

    def stop(self):
        sys.settrace(None)
        self.conn.close()
        print(f"[PyChronicle] Execution traced successfully! Total steps logged: {self.step_count}")

def time_travel_debug(func):
    def wrapper(*args, **kwargs):
        tracer = PyChronicleTracer()
        tracer.start()
        try:
            result = func(*args, **kwargs)
        finally:
            tracer.stop()
        return result
    return wrapper