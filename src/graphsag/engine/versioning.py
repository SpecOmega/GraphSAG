from __future__ import annotations
import re
class VersionError(ValueError): pass

def parse_version(value):
    m=re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+].*)?',value)
    if not m: raise VersionError('INVALID_VERSION')
    return tuple(map(int,m.groups()))

def require_monotonic(old,new):
    if parse_version(new) <= parse_version(old): raise VersionError('VERSION_NOT_MONOTONIC')
