from __future__ import annotations
import sqlite3, threading, json
from graphsag.domain.models import AuditEvent
from graphsag.engine.audit import AuditSink
class SQLiteAuditSink(AuditSink):
    def __init__(self,path='graphsag-audit.db'):
        self.db=sqlite3.connect(path,check_same_thread=False,isolation_level='IMMEDIATE'); self.lock=threading.Lock()
        self.db.execute('PRAGMA journal_mode=WAL'); self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS audit_events(event_id TEXT PRIMARY KEY,event_hash TEXT NOT NULL,ts REAL NOT NULL,event_json TEXT NOT NULL)'); self.db.commit()
    def commit(self,event:AuditEvent):
        with self.lock:
            try:
                self.db.execute('INSERT OR IGNORE INTO audit_events VALUES(?,?,?,?)',(event.event_id,event.digest(),event.ts,json.dumps(event.canonical(),sort_keys=True,separators=(",",":"))))
                self.db.commit(); return True
            except Exception: self.db.rollback(); return False
    def close(self): self.db.close()
