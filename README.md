# HSM Onboard exercices

Docs:
- https://developer.hashicorp.com/vault/tutorials/encryption-as-a-service/eaas-transit
- https://cloud.google.com/kms/docs/hsm
- https://developer.hashicorp.com/vault/docs/secrets/transit#tutorial


Prerequsites:
- [devbox:](https://www.jetify.com/docs/devbox/quickstart/#install-devbox)
Devbox is a wrapper around `nix`. This simplifies a lot the local developmen
with nix.

```bash
curl -fsSL https://get.jetify.com/devbox | bash
```

# ed25519 
0. Run the development shell with devbox. This will 
- install the python
- install `vault`
- create a virtual environment
- install required libries in the virtual environment

```bash
devbox shell

Info: Ensuring packages are installed.
✓ Computed the Devbox environment.
Starting a devbox shell...
Directory exists but is not a valid virtual environment. Creating a new one...
Collecting hvac
  Using cached hvac-2.3.0-py3-none-any.whl (155 kB)
Collecting asyncio
  Using cached asyncio-3.4.3-py3-none-any.whl (101 kB)
Collecting requests<3.0.0,>=2.27.1
  Using cached requests-2.32.3-py3-none-any.whl (64 kB)
Collecting idna<4,>=2.5
  Using cached idna-3.10-py3-none-any.whl (70 kB)
Collecting certifi>=2017.4.17
  Using cached certifi-2024.12.14-py3-none-any.whl (164 kB)
Collecting charset-normalizer<4,>=2
  Using cached charset_normalizer-3.4.0-cp39-cp39-macosx_11_0_arm64.whl (120 kB)
Collecting urllib3<3,>=1.21.1
  Using cached urllib3-2.2.3-py3-none-any.whl (126 kB)
Installing collected packages: asyncio, urllib3, idna, charset-normalizer, certifi, requests, hvac
Successfully installed asyncio-3.4.3 certifi-2024.12.14 charset-normalizer-3.4.0 hvac-2.3.0 idna-3.10 requests-2.32.3 urllib3-2.2.3

[notice] A new release of pip is available: 23.0.1 -> 24.3.1
[notice] To update, run: pip install --upgrade pip
```

1. Set up HashiCorp Vault - Local
Termianl 1:start vault server

```bash
vault server -dev -dev-listen-address="127.0.0.1:8200"
```
in another terminal

Enable the Transit secrets engine:
```bash
export VAULT_ADDR='http://127.0.0.1:8200'
vault secrets enable transit
```

2. Create a named encryption key:
```bash
vault write -f transit/keys/radu-key-ed25519 type=ed25519
```

Usage example

Encrypt some plaintext data using the /encrypt endpoint with a named key:

NOTE: All plaintext data must be base64-encoded. The reason for this requirement is that Vault does not require that the plaintext is "text". It could be a binary file such as a PDF or image. The easiest safe transport mechanism for this data as part of a JSON payload is to base64-encode it.

```bash
vault write transit/encrypt/radu-key plaintext=$(echo "radu secret data" | base64)

Key            Value
---            -----
ciphertext     vault:v1:CSWbr73d3diG1O8i0XGkUvsY7Apor+Zilwyh2okdOHBpAPnE4KmHtQgBZSU2
key_version    1
```

decrypt
```bash

vault write transit/decrypt/radu-key ciphertext=vault:v1:CSWbr73d3diG1O8i0XGkUvsY7Apor+Zilwyh2okdOHBpAPnE4KmHtQgBZSU2
Key          Value
---          -----
plaintext    cmFkdSBzZWNyZXQgZGF0YQo=

echo cmFkdSBzZWNyZXQgZGF0YQo= | base64 -d
radu secret data
```


3. Run the app
```bash
./app.py
Processing Actions...

Signing Message: b'Hello, Vault!'
Signature: 3f1ab8dc77f5c2d2674e0bd6d3235e790cf8bffb5d41a8b9673fc5c459dd764590f5234792bdd66ae37b5e2010b9d6a97828d4941bd46a40d11276ff563f8901

Signing Message: b'This is another test message.'
Signature: 94e074263e9964f771740ee74e913a471fc734bab804b0bc9e15c62ca1b70a5acb8ecc227a4ecc387b1d4051f5b1d884202bf158088acf1dc9d3c8c4fbd9ef0e

Verifying Message: b'Hello, Vault!'
With Signature: 00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
Verification Result: False
```
