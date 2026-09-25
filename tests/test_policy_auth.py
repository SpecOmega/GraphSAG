from graphsag.engine.policy import Policy,PolicyStore
from graphsag.engine.auth import StaticPrincipalVerifier,Principal,AuthenticationError
from graphsag.engine.idempotency import IdempotencyStore
from graphsag.domain.models import RiskLevel
def test_policy_monotonic_version():
 s=PolicyStore(Policy('1')); s.publish(Policy('2'))
 try: s.publish(Policy('1')); assert False
 except ValueError: pass
def test_auth_scope():
 v=StaticPrincipalVerifier({'u':Principal('u',frozenset({'decide'}))}); assert v.verify('u','decide').principal_id=='u'
 try: v.verify('u','execute'); assert False
 except AuthenticationError: pass
def test_idempotency():
 s=IdempotencyStore(); assert s.reserve('x'); assert not s.reserve('x')
