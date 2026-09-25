from __future__ import annotations
import sqlite3, threading, json, hashlib
from graphsag.domain.models import AuditEvent

class ChainAuditSink:
    def __init__(self,path=':memory:'):
        self.db=sqlite3.connect(path,check_same_thread=False,isolation_level='IMMEDIATE'); self.db.execute('PRAGMA journal_mode=WAL'); self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS audit_chain(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE,event_hash TEXT NOT NULL,prev_hash TEXT NOT NULL,event_json TEXT NOT NULL)'); self.db.commit(); self._lock=threading.Lock()
    def commit(self,event: AuditEvent):
        with self._lock:
            row=self.db.execute('SELECT event_hash FROM audit_chain ORDER BY seq DESC LIMIT 1').fetchone(); prev=row[0] if row else '0'*64
            event_hash=hashlib.sha256((prev+event.digest()).encode()).hexdigest()
            try: self.db.execute('INSERT INTO audit_chain(event_id,event_hash,prev_hash,event_json) VALUES(?,?,?,?)',(event.event_id,event_hash,prev,json.dumps(event.canonical(),sort_keys=True,separators=(',',':')))); self.db.commit(); return True
            except sqlite3.IntegrityError: self.db.rollback(); return False
    def verify(self):
        prev='0'*64
        for event_hash, prev_hash, event_json in self.db.execute('SELECT event_hash,prev_hash,event_json FROM audit_chain ORDER BY seq'):
            if prev_hash!=prev: return False
            event=hashlib.sha256(json.dumps(json.loads(event_json),sort_keys=True,separators=(',',':')).encode()).hexdigest()
            prev=hashlib.sha256((prev+event).encode()).hexdigest()
            if prev!=event_hash: return False
        return True
