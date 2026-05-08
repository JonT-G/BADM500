"""Cryptographic helpers for ActivityPub HTTP Signatures.

The ActivityPub requires that each Actor has a public/private keypair,
and that outgoing requests to other servers are signed with the private key using HTTP Signatures. 
Module generates keypair and provides helper functions for signing requests, which are used in federation/http_signatures.py.
used: https://dev.to/aaronktberry/generating-encrypted-key-pairs-in-python-69b
"""

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa



def generate_actor_keypair():
    """
    Return (private_pem, public_pem) for a new Actor.
    RSA 2048 with PKCS#8 format with no encryption.
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode('utf-8')
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode('utf-8')
    return private_pem, public_pem