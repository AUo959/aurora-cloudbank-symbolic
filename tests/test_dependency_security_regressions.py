"""Dependency boundary regressions for shared JWT verification state."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest


@pytest.mark.security
def test_unverified_decode_does_not_poison_later_verified_claim_checks():
    key = 'dependency-regression-test-key-with-sufficient-length'
    expired = jwt.encode({'sub': 'reader', 'exp': datetime.now(timezone.utc) - timedelta(hours=1)}, key, algorithm='HS256')
    options = {'verify_signature': False}
    jwt.decode(expired, options=options)
    assert options == {'verify_signature': False}
    options['verify_signature'] = True
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired, key, algorithms=['HS256'], options=options)
    valid = jwt.encode({'sub': 'reader', 'exp': datetime.now(timezone.utc) + timedelta(hours=1)}, key, algorithm='HS256')
    assert jwt.decode(valid, key, algorithms=['HS256'], options=options)['sub'] == 'reader'
