# Riot take-home challenge

The project is made in python using Flask, swagger and apispec.
Design notes are available below to detail some choices.

## Usage

### Demonstration API

A working demo of the API is available here
[https://riot-takehome-production.up.railway.app/](https://riot-takehome-production.up.railway.app/).

Default payloads are valid ones, and work as pair between `encrypt`/`decrypt` endpoints, and `sign`/`verify`.

### Running the app locally

You can also run the Flask app locally. It will default to `http://127.0.0.1:5000`. Using `virtualenv` :

```bash
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
flask run
```

> Note that the signature algorithm needs a `HMAC_SECRET` environment variable. If it is not set, it will default to an
> empty string, so the signatures won't be the same as the ones from the demonstration API.

If you want to run the tests :

```bash
pip install -r requirements-ci.txt
python -m pytest tests/unit
python -m pytest tests/functional
```

## Files structure

### API

All relevant code lies in `api` module. Here's the detail by relevance order.

* `controllers` holds the controllers that actually do the business logic
    + `encryption.py` holds the handler for `/encrypt` and `/decrypt` endpoints
    + `signature.py` holds the handler for `/sign` and `/verify` endpoints
* `helpers` holds the algorithm classes for encryption and signature, see *Design notes* below for explanations
* `services` holds the routes definition for the endpoints, no logic there except request validation and error handling
* `config` contains various configurations (api spec, json fields and constants). The secret key for the signing
    algorithm is read there, from the `HMAC_SECRET` environment variable

### Tests

The `tests` folder contains `unit` and `functional` tests.

* Unit tests are made on the controllers and the helpers, with mocking relevant methods
* Functional tests are made on the endpoints themselves (services). This is where we test the roundtrip validation :
    + `/decrypt` successfully handles the output of `/encrypt`, with additional clear values
    + `/verify` successfully verifies an input signed by us with `/sign`
    + `/verify` successfully refuses tampered data or invalid signature
    + `/verify` successfully verifies two equivalent payloads with the same signature

## Design notes

Below are explanations about some architectural or functional choices I made for the exercise.

### Usage of a sentinel to detect encrypted values

As the `decrypt` endpoint must be able to distinguish between encrypted values and clear ones, I chose to use a sentinel
string, prefixed to the encrypted values. This mimics what happens for PGP messages or RSA keys.

The idea is that the cryptographic security is provided by the chosen encryption algorithm, and the sentinel is only
there to signal an encrypted value for later calls to `/decrypt` endpoint.

There's a slight risk of collision with a clear value that would actually be prefixed with the sentinel. Knowing more
about the API business context would suffice to choose an even better sentinel. 

### Abstraction

The objective is to be able to change the encryption or signature algorithms easily without having to change many parts
of the code. The reasoning is the same for encryption and signatures, we use encryption as example.

The controllers `EncryptionHandler` and `SignatureHandler` take an algorithm helper as argument.
See `api/services/encryption.py` :

```python
from api.helpers.crypters import Base64Crypter

handler = EncryptionHandler(crypter=Base64Crypter())
```

This allows to easily change the encryption algorithm by just using another algorithm helper. For instance, if we had
a `RSACrypter`, we would just have to update the endpoint code to :

```python
from api.helpers.crypters import RSACrypter

handler = EncryptionHandler(crypter=RSACrypter())
```

The only constraint is that any algorithm helper must contain `encrypt` and `decrypt` methods, as the class `RootCrypter`
indicates, so that the encryption controller can use it whatever the algorithm helper chosen.

This architecture allows to maintain several algorithms in the codebase, and why not choose dynamically which algorithm
to use for encryption (this would require adding a query parameter in the endpoint though).

Another simpler, but less flexible, option would be a fixed algorithm helper, and just updating its `encrypt` and
`decrypt` method, while the sentinel logic would stay the same in the controller.

### Allowing any key ordering for signature

I used the canonical representation of the given payload to make the signature independant of the order of keys. Before
creating the signature, the JSON is serialized to its canonical version : most compact form and ordered keys (recursively).

This allows payloads with the same items but in different orders to have the same serialized version, thus the same
signature.

### Storage of HMAC key

The key used in the HMAC signing algorithm is read as an environment variable. I generated a 256-bit secret using the
`secrets` module, and stored it as sealed variable in the railway environment, so there's no access to the key either in
the code or in the logs. For the encryption service, improving to an algorithm such as RSA would follow the same
principles.

If you run the app locally without having a `HMAC_SECRET` environment variable set, the `HMACSigner` will log a warning
but the endpoints would still work, using an empty string as the algorithm key.
