from graphsag.storage.sqlite_audit import SQLiteAuditSink
from graphsag.domain.models import AuditEvent
def test_audit_idempotent(tmp_path):
 s=SQLiteAuditSink(str(tmp_path/'a.db')); e=AuditEvent('e','x','q',None,{'a':1}); assert s.commit(e); assert s.commit(e); assert s.db.execute('select count(*) from audit_events').fetchone()[0]==1; s.close()
