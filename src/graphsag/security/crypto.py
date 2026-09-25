from __future__ import annotations
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import base64

class SignatureError(ValueError): pass

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')

def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + '=' * (-len(value) % 4))

@dataclass(frozen=True)
class Ed25519Signer:
    private_key: Ed25519PrivateKey
    key_id: str
    @classmethod
    def generate(cls, key_id: str = 'local-dev') -> 'Ed25519Signer':
        return cls(Ed25519PrivateKey.generate(), key_id)
    def sign(self, message: bytes) -> str:
        return _b64(self.private_key.sign(message))
    def public_key_bytes(self) -> bytes:
        return self.private_key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

@dataclass(frozen=True)
class Ed25519Verifier:
    keys: dict[str, bytes]
    def verify(self, key_id: str, message: bytes, signature: str) -> None:
        raw = self.keys.get(key_id)
        if raw is None: raise SignatureError('UNKNOWN_SIGNING_KEY')
        try: Ed25519PublicKey.from_public_bytes(raw).verify(_unb64(signature), message)
        except Exception as exc: raise SignatureError('SIGNATURE_INVALID') from exc
