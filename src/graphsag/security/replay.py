from __future__ import annotations
import sqlite3, threading, time

class ReplayError(ValueError): pass

class ReplayStore:
    def reserve(self, nonce: str, expires_at: float) -> bool: raise NotImplementedError

class MemoryReplayStore(ReplayStore):
    def __init__(self): self._items={}; self._lock=threading.Lock()
    def reserve(self, nonce, expires_at):
        now=time.time()
        with self._lock:
            self._items={k:v for k,v in self._items.items() if v>now}
            if nonce in self._items: return False
            self._items[nonce]=expires_at; return True

class SQLiteReplayStore(ReplayStore):
    def __init__(self, path=':memory:'):
        self.db=sqlite3.connect(path, check_same_thread=False, isolation_level='IMMEDIATE')
        self.db.execute('PRAGMA journal_mode=WAL'); self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS replay(nonce TEXT PRIMARY KEY, expires_at REAL NOT NULL)'); self.db.commit()
        self._lock=threading.Lock()
    def reserve(self, nonce, expires_at):
        with self._lock:
            now=time.time(); self.db.execute('DELETE FROM replay WHERE expires_at<=?',(now,))
            try:
                self.db.execute('INSERT INTO replay(nonce,expires_at) VALUES(?,?)',(nonce,expires_at)); self.db.commit(); return True
            except sqlite3.IntegrityError:
                self.db.rollback(); return False
