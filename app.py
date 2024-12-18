#!/usr/bin/env python
import hvac
import asyncio
import base64
from typing import List, Optional, Dict, Union

# -------------------
# Helper Functions
# -------------------


def to_base64(data: Union[str, bytes]) -> str:
    """Convert data to a base64-encoded string."""
    if isinstance(data, str):
        data = data.encode()
    return base64.b64encode(data).decode()


def from_base64(data: str) -> bytes:
    """Convert base64-encoded string back to bytes."""
    return base64.b64decode(data)


def initialize_vault_client(vault_addr: str, token: str):
    """Initialize HashiCorp Vault client."""
    client = hvac.Client(url=vault_addr, token=token)
    if not client.is_authenticated():
        raise Exception("Failed to authenticate with HashiCorp Vault.")
    return client


async def vault_sign(client, key_name: str, message: bytes) -> bytes:
    """Sign a message using HashiCorp Vault Transit Secret Engine."""
    response = client.secrets.transit.sign_data(
        name=key_name,
        hash_input=to_base64(message),
    )
    # Vault returns the signature as "vault:v1:base64..."
    signature = response["data"]["signature"]
    return from_base64(signature.split(":")[-1])


async def vault_verify(
    client, key_name: str, message: bytes, signature: bytes
) -> bool:
    """Verify a message signature using HashiCorp Vault Transit Secret Engine."""
    response = client.secrets.transit.verify_signed_data(
        name=key_name,
        hash_input=to_base64(message),
        signature=f"vault:v1:{to_base64(signature)}",
    )
    return response["data"]["valid"]


# -------------------
# Message Stream
# -------------------


async def action_stream(actions: List[Dict]):
    """
    Simulate a stream of messages to be signed or verified.
    Each action can either be:
      - {"action": "sign", "message": <bytes>}
      - {"action": "verify", "message": <bytes>, "signature": <bytes>}
    """
    for action in actions:
        yield action


# -------------------
# Application Logic
# -------------------


async def process_actions(stream, client, key_name: str):
    """
    Process a stream of actions to sign or verify messages.

    Parameters:
      - stream: An async generator providing actions.
      - client: Initialized Vault client.
      - key_name: The name of the key in Vault Transit Secrets Engine.
    """
    async for action in stream:
        if action["action"] == "sign":
            message = action["message"]
            print(f"\nSigning Message: {message}")
            signature = await vault_sign(client, key_name, message)
            print(f"Signature: {signature.hex()}")

        elif action["action"] == "verify":
            message = action["message"]
            signature = action["signature"]
            print(f"\nVerifying Message: {message}")
            print(f"With Signature: {signature.hex()}")
            result = await vault_verify(client, key_name, message, signature)
            print(f"Verification Result: {result}")


# -------------------
# Main Function
# -------------------


async def main():
    # Configuration
    VAULT_ADDR = "http://127.0.0.1:8200"
    VAULT_TOKEN = "hvs.tG9A3rTdMrMuk4a6NQ8qqZRf"  # Root token
    KEY_NAME = "radu-key-ed25519"

    # Initialize Vault client
    client = initialize_vault_client(VAULT_ADDR, VAULT_TOKEN)

    # Simulated stream of actions
    actions = [
        {"action": "sign", "message": b"Hello, Vault!"},
        {"action": "sign", "message": b"This is another test message."},
        {
            "action": "verify",
            "message": b"Hello, Vault!",
            "signature": b"\x00" * 64,
        },  # Invalid signature
    ]

    # Process the stream
    print("Processing Actions...")
    await process_actions(action_stream(actions), client, KEY_NAME)


# -------------------
# Run Application
# -------------------

if __name__ == "__main__":
    asyncio.run(main())
