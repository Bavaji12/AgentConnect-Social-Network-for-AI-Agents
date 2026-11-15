import pytest
from app.core.security import sign_webhook_payload, verify_webhook_signature
from app.security.ssrf import validate_webhook_url
from app.core.config import settings

def test_webhook_hmac_signing_and_verification():
    payload = '{"event_id":"evt_123","post_id":"post_456","score":0.89}'
    secret = "my-secret-key-12345"

    sig = sign_webhook_payload(payload, secret=secret)
    assert sig.startswith("sha256=")

    # Verification should succeed with identical payload and secret
    assert verify_webhook_signature(payload, sig, secret=secret) is True

    # Tampered payload must fail
    tampered = '{"event_id":"evt_123","post_id":"post_456","score":0.99}'
    assert verify_webhook_signature(tampered, sig, secret=secret) is False

    # Wrong signature header must fail
    assert verify_webhook_signature(payload, "sha256=invalidhash", secret=secret) is False

def test_webhook_ssrf_blocking():
    # Save original setting
    orig_allow = settings.ALLOW_PRIVATE_IPS
    try:
        # Enable strict production mode
        settings.ALLOW_PRIVATE_IPS = False

        # Non-http scheme
        is_safe, msg = validate_webhook_url("ftp://example.com/webhook")
        assert is_safe is False

        # Localhost blocking
        is_safe, msg = validate_webhook_url("http://localhost:8080/webhook")
        assert is_safe is False
        assert "localhost" in msg.lower() or "blocked" in msg.lower()

        # Cloud metadata IP blocking
        is_safe, msg = validate_webhook_url("http://169.254.169.254/latest/meta-data")
        assert is_safe is False
        assert "metadata" in msg.lower() or "restricted" in msg.lower()

        # Valid public IP / URL
        is_safe, msg = validate_webhook_url("https://93.184.216.34/webhooks/agent")
        assert is_safe is True
    finally:
        settings.ALLOW_PRIVATE_IPS = orig_allow
