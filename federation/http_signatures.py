"""
Module for signing outbound HTTP requests with HTTP Signatures, and verifying signatures on inbound requests:
  - sign_request_headers: builds Date / Digest / Signature headers for an
    outbound POST so receivers can verify it came from us.
  - verify_request: given an inbound request and a public key PEM, returns
    True iff the Signature header is valid.

Algorithm is rsa-sha256. Body integrity is covered by an SHA-256 Digest
header that is included in the signed-headers list.
"""

import base64
import email.utils
import hashlib
import re
from urllib.parse import urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


# Headers we always sign on outbound POSTs.
OUTBOUND_SIGNED_HEADERS = ['(request-target)', 'host', 'date', 'digest']

_SIG_HEADER_RE = re.compile(r'(\w+)="([^"]*)"')


def digest_header(body: bytes) -> str:
    """Build the value for the Digest header. SHA-256 in base64."""
    digest = hashlib.sha256(body).digest()
    return f"SHA-256={base64.b64encode(digest).decode('ascii')}"


def _build_signing_string(method: str, path: str, header_names, header_values) -> bytes:
    """
    Build the string that is signed for HTTP Signatures, based on the list of header names and their values.
    """
    lines = []
    for name in header_names:
        if name == '(request-target)':
            lines.append(f"(request-target): {method.lower()} {path}")
        else:
            value = header_values.get(name.lower())
            if value is None:
                raise KeyError(f"signed-headers list references missing header: {name}")
            lines.append(f"{name}: {value}")
    return '\n'.join(lines).encode('utf-8')


def sign_request_headers(method: str, url: str, body: bytes, key_id: str, private_key_pem: str) -> dict:
    """
    Return the headers that authenticate an outbound POST.
    """
    parts = urlsplit(url)
    host = parts.netloc
    path = parts.path or '/'
    if parts.query:
        path = f"{path}?{parts.query}"

    date = email.utils.formatdate(usegmt=True)
    digest = digest_header(body)

    header_values = {'host': host, 'date': date, 'digest': digest}
    string_to_sign = _build_signing_string(method, path, OUTBOUND_SIGNED_HEADERS, header_values)

    private_key = serialization.load_pem_private_key(
        private_key_pem.encode('utf-8'),
        password=None,
    )
    signature = private_key.sign(string_to_sign, padding.PKCS1v15(), hashes.SHA256())
    signature_b64 = base64.b64encode(signature).decode('ascii')

    signed_headers_str = ' '.join(OUTBOUND_SIGNED_HEADERS)
    signature_header = (
        f'keyId="{key_id}",algorithm="rsa-sha256",'
        f'headers="{signed_headers_str}",signature="{signature_b64}"'
    )

    return {
        'Host': host,
        'Date': date,
        'Digest': digest,
        'Signature': signature_header,
    }


def parse_signature_header(value: str) -> dict:
    """Parse a Signature header into its components. Returns a dict of the key=value pairs in the header, with quotes stripped."""
    return dict(_SIG_HEADER_RE.findall(value))


def verify_request(method: str, path: str, headers: dict, body: bytes, public_key_pem: str) -> bool:
    """
    Verify an incoming request with the given public key. 
    Returns True if the Signature header is valid for the request, False otherwise.
    """
    lower_headers = {k.lower(): v for k, v in headers.items()}

    sig_header = lower_headers.get('signature')
    if not sig_header:
        return False
    parsed = parse_signature_header(sig_header)

    algorithm = parsed.get('algorithm', 'rsa-sha256')
    if algorithm not in ('rsa-sha256', 'hs2019'):
        return False

    signature_b64 = parsed.get('signature', '')
    if not signature_b64:
        return False

    signed_names = parsed.get('headers', '(request-target) host date').split()

    # If digest was signed, verify the body matches.
    if 'digest' in signed_names:
        if lower_headers.get('digest') != digest_header(body):
            return False

    try:
        string_to_verify = _build_signing_string(method, path, signed_names, lower_headers)
    except KeyError:
        return False

    public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            string_to_verify,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except InvalidSignature:
        return False
    return True


def key_id_to_actor_uri(key_id: str) -> str:
    """Given a keyId like "https://example.com/users/alice#main-key", return the actor URI "https://example.com/users/alice"."""
    return key_id.split('#', 1)[0]
