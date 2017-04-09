<img src="http://i.imgur.com/ZymFZd8.jpg" width="400"/>

# NoDB

[![Build Status](https://travis-ci.org/Miserlou/NoDB.svg)](https://travis-ci.org/Miserlou/NoDB)
[![Coverage](https://img.shields.io/coveralls/Miserlou/NoDB.svg)](https://coveralls.io/github/Miserlou/NoDB)
[![PyPI](https://img.shields.io/pypi/v/NoDB.svg)](https://pypi.python.org/pypi/nodb)
[![Slack](https://img.shields.io/badge/chat-slack-ff69b4.svg)](https://slack.zappa.io/)
[![Gun.io](https://img.shields.io/badge/made%20by-gun.io-blue.svg)](https://gun.io/)
[![Patreon](https://img.shields.io/badge/support-patreon-brightgreen.svg)](https://patreon.com/zappa)

_NoDB isn't a database.. but it sort of looks like one!_

**NoDB** an incredibly simple, Pythonic object store based on Amazon's S3 static file storage.

It's useful for **prototyping**, **casual hacking**, and (maybe) even low-traffic **server-less backends**!

## Features

* Schema-less!
* Server-less!
* Uses S3 as a datastore.
* Loads to native Python objects with `cPickle`
* Alternately use JSON as a storage format for untrusted data
* Cheap!
* Fast(ish)

## Installation

**NoDB** can be installed easily via `pip`, like so:

```
$ pip install nodb
```

## Warning!
**NoDB** is **insecure by default**! Do not use it for untrusted data before setting `serializer` to `"json"`!

## Usage

**NoDB** is super easy to use!

You simply make a NoDB object, point it to your bucket and tell it what field you want to index on.

```python
# Set it up
from nodb import NoDB

nodb = NoDB()
nodb.bucket = "my-s3-bucket"
nodb.index = "Name"
```

After that, you can save and load literally anything you want, whenever you want!

```python
# Save an object!
user = {"Name": "Jeff", "age": 19}
nodb.save(user)

# Load our object!
user = nodb.load("Jeff")
print user.age # 19
```

By default, you can save and load any Python object.

## Advanced Usage

#### Different Serializers

To use a safer, non-Pickle serializer, just set JSON as your serializer:

```python
nodb = NoDB()
nodb.serializer = "json"
```

### Object Metadata

You can get metainfo (datetime and UUID) for a given object by passing `metainfo=True` to `load`, likek so:

```python
# Load our object and metainfo!
user, datetime, uuid = nodb.load("Jeff", metainfo=True)
```

#### Human Readable Indexes

By default, the indexes are hashed. If you want to be able to debug through the AWS console, set `human_readable_indexes` to True:

```python
nodb.human_readable_indexes = True
```

## TODO (Maybe?)

* **Tests** with Placebo
* **Python3** support
* Local file storage
* Quering ranges (numberic IDs only), etc.
* Different serializers
* Custom serializers
* Multiple indexes
* Compression
* Bucket management

## Related Projects

* [Zappa](https://github.com/Miserlou/Zappa) - Python's server-less framework!
* [K.E.V.](https://github.com/capless/kev) - a Python ORM for key-value stores based on Redis, S3, and a S3/Redis hybrid backend.

## Contributing

This project is still young, so there is still plenty to be done. Contributions are more than welcome!

Please file tickets for discussion before submitting patches. Pull requests should target `master` and should leave NoDB in a "shippable" state if merged.

If you are adding a non-trivial amount of new code, please include a functioning test in your PR. For AWS calls, we use the `placebo` library, which you can learn to use [in their README](https://github.com/garnaat/placebo#usage-as-a-decorator). The test suite will be run by [Travis CI](https://travis-ci.org/Miserlou/NoDB) once you open a pull request.

Please include the GitHub issue or pull request URL that has discussion related to your changes as a comment in the code ([example](https://github.com/Miserlou/Zappa/blob/fae2925431b820eaedf088a632022e4120a29f89/zappa/zappa.py#L241-L243)). This greatly helps for project maintainability, as it allows us to trace back use cases and explain decision making.

## License

(C) Rich Jones 2017, MIT License.
