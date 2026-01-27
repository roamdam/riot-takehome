# Riot take-home challenge

The project is made in python using Flask, swagger and apispec.
Design notes are available below to detail somes choices.
On top of the tests suite, the section below gives some example requests to test functionality and consistency.

## Usage

### Demonstration API

A working demo of the API is available here
[https://riot-takehome-production.up.railway.app/](https://riot-takehome-production.up.railway.app/).

Default payloads are valid ones, and work as pair between `encrypt`/`decrypt` endpoints, and `sign`/`verify`.

### Running the app locally

You can also run the Flask app locally. With the requirements installed, it will default to `http://127.0.0.1:5000` :

```bash
pip install -r requirements.txt
flask run
```

From there, here are some ready-to-execute requests :

#### Encrypt / Decrypt

```bash
# Encrypt
curl -X POST http://127.0.0.1:5000/api/encrypt -H 'Content-Type: application/json' -d '{"Hello": "world"}'
# Decrypt return from encrypt
curl -X POST http://127.0.0.1:5000/api/decrypt -H 'Content-Type: application/json' -d '{"Hello":"@@enc@@v1::IndvcmxkIg=="}'
# Decrypt return from encrypt with an added clear field
curl -X POST http://127.0.0.1:5000/api/decrypt -H 'Content-Type: application/json' -d '{"Hello":"@@enc@@v1::IndvcmxkIg==", "from": "earth"}'
```

#### Sign / verify

```bash
# Sign
curl -X POST http://127.0.0.1:5000/api/sign -H 'Content-Type: application/json' -d '{"Hello": "world"}'
# Verify with returned signature
curl -X POST http://127.0.0.1:5000/api/verify -H 'Content-Type: application/json' -d '{"data": {"Hello": "world"}, "signature":"5b1ffef543e790b14d5b283f8205cccad151d3f7d05829b79f76541d1ef71eba"}'
# Verify with tampered data
curl -X POST http://127.0.0.1:5000/api/verify -H 'Content-Type: application/json' -d '{"data": {"Hi": "world"}, "signature":"5b1ffef543e790b14d5b283f8205cccad151d3f7d05829b79f76541d1ef71eba"}'

# Verify identical JSON with varying ordering
curl -X POST http://127.0.0.1:5000/api/verify -H 'Content-Type: application/json' -d '{"data": {"me": "here", "you": "there"}, "signature": "15cd5d148d56732a0d52e0f352c789a4fc738b7b6bed0b66cfd3f8461eaf14df"}'
curl -X POST http://127.0.0.1:5000/api/verify -H 'Content-Type: application/json' -d '{"data": {"you": "there", "me": "here"}, "signature": "15cd5d148d56732a0d52e0f352c789a4fc738b7b6bed0b66cfd3f8461eaf14df"}'

```

## Design notes

Below are explanations about some architectural or functional choices I made for the exercise.

### Abstraction

The objective is to be able to change the encryption or signature algorithms easily without having to change many parts
of the code. The reasoning is the same for encryption and signatures, we use encryption as example.

The controllers `EncryptionHandler` and `SignatureHandler` takes an algorithm helper as argument :

```python
from api.helpers.crypters import SomeCrypter

handler = EncryptionHandler(crypter=SomeCrypter())
```

Provided the algorithm helper contains an `encrypt` and `decrypt` method, it allows to easily change the algorithm used
by the controller, by writing a new helper with the desired algorithm and changing the parameter in the above line.

This would even allow to maintain several algorithms in the codebase without many changes, allowing evolution with
retro-compatibility, and why not exposing a query parameter in the API to choose the algorithm dynamically.

Another simpler option would have been to use a unique helper class, not given as parameter. Changing the algorithm would
only require changing the content of the helper's `encrypt` and `decrypt` methods, but we would lose the possibility of
maintaining several algorithms.

### Usage of a sentinel to detect encrypted values

As the `decrypt` endpoint must be able to distinguish between encrypted values and clear ones, I chose to use a sentinel
string, prefixed to the encrypted values. The role of this sentinel is to signal that the value was encrypted by us,
allowing an easy detection without compromising the encryption, which is provided by the encryption algorithm on
the value itself.

If the sentinel isn't there, we know it's not encrypted. If it's there, we try and decrypt the value. The endpoint will
return a `BadRequest` if any encrypted string cannot be decrypted, meaning the string was not an encrypted value returned
by us previously.

The choice of the sentinel value emerges from two ideas:

* avoid collision with clear strings. This would be business/domain dependant, but as an generic example I used
`@@enc@@vX::`. The versioning would, for instance, allow to link various encryption algorithm behind the scenes.
* allow easy reading by humans, in the code or in the logs. 

### Allowing any key ordering for signature

I used the canonical representation of the given payload to make the signature independant of the order of keys. Before
creating the signature, the JSON is serialized to its canonical version : most compact form and ordered keys (recursively).

This allows payloads with the same items but in different orders to have the same seriliazed version, and then the same
signature.

### Storage of HMAC key

The key used in the HMAC signing algorithm is read as an environment variable. I generated a 256-bit secret using the
`secrets` module, and stored it as sealed variable in the railway environment, so there's no access to the key either in
the code or in the logs. For the encryption service, improving to an algorithm such as RSA would follow the same
principles.

If you run the app locally without having a `HMAC_SECRET` environment variable set, the `HMACSigner` will log a warning
but the endpoints would still work, using an empty string as the algorithm key.
