from nacl.public import PrivateKey, Box, PublicKey
from base64 import a85encode, a85decode
from ecies.utils import aes_decrypt, aes_encrypt


def _hex_to_bytes(hex: str) -> bytes:
    return bytes.fromhex(hex if hex[:2] == "0x" else hex)


def export_public_key(private_key_hex: str) -> bytes:
    """Export public key for contract join request.

    Args:
        private_key: hex string representing private key

    Returns:
        32 bytes representing public key
    """
    return bytes(PrivateKey(_hex_to_bytes(private_key_hex)).public_key)


def encrypt_nacl(public_key: bytes, data: bytes) -> bytes:
    """Encryption function using NaCl box compatible with MetaMask
    For implementation used in MetaMask look into: https://github.com/MetaMask/eth-sig-util

    Args:
        public_key: public key of recipient
        data: message data

    Returns:
        encrypted data
    """
    emph_key = PrivateKey.generate()
    enc_box = Box(emph_key, PublicKey(public_key))
    # Encryption is required to work with MetaMask decryption (requires utf8)
    data = a85encode(data)
    ciphertext = enc_box.encrypt(data)
    return bytes(emph_key.public_key) + ciphertext


def decrypt_nacl(private_key: bytes, data: bytes) -> bytes:
    """Decryption function using NaCl box compatible with MetaMask
    For implementation used in MetaMask look into: https://github.com/MetaMask/eth-sig-util

    Args:
        private_key: private key to decrypt with
        data: encrypted message data

    Returns:
        decrypted data
    """
    emph_key, ciphertext = data[:32], data[32:]
    box = Box(PrivateKey(private_key), PublicKey(emph_key))
    return a85decode(box.decrypt(ciphertext))


def encrypt_bytes(bytes: bytes, secret: bytes) -> bytes:
    """Encrypt bytes (model) for storing in contract/IPFS."""
    return aes_encrypt(secret, bytes)


def decrypt_bytes(ciphertext: bytes, secret: bytes) -> bytes:
    """Decrypt bytes (model) stored in contract/IPFS."""
    return aes_decrypt(secret, ciphertext)