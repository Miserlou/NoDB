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

It's useful for **prototyping**, **casual hacking**, and (maybe) even low-traffic **server-less backends** for **[Zappa](https://github.com/Miserlou/Zappa) apps**!

## Features

* Schema-less!
* Server-less!
* Uses S3 as a datastore.
* Loads to native Python objects with `cPickle`
* Can use JSON as a serialization format for untrusted data
* Local filestore based caching
* Cheap(ish)!
* Fast(ish)! (Especially from Lambda)

## Performance

Initial load test with [Goad](https://goad.io/) of 10,000 requests (500 concurrent) with a write and subsequent read of the same index showed an average time of 400ms. This should be more than acceptable for many applications, even those which don't have sparse data, although that is preferred.

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
from nodb import NoDB

nodb = NoDB()
nodb.bucket = "my-s3-bucket"
nodb.index = "name"
```

After that, you can save and load literally anything you want, whenever you want!

```python
# Save an object!
user = {"name": "Jeff", "age": 19}
nodb.save(user) # True

# Load our object!
user = nodb.load("Jeff")
print(user['age']) # 19

# Delete our object
nodb.delete("Jeff") # True
```

By default, you can save and load any Python object.

Here's the same example, but with a class. Note the import and configuration is the same!

```python
class User(object):
    name = None
    age = None

    def print_name(self):
        print("Hi, I'm " + self.name + "!")

new_user = User()
new_user.name = "Jeff"
new_user.age = 19
nodb.save(new_user) # True

jeff = nodb.load("Jeff")
jeff.print_name() # Hi, I'm Jeff!
```

## Advanced Usage

### Different Serializers

To use a safer, non-Pickle serializer, just set JSON as your serializer:

```python
nodb = NoDB()
nodb.serializer = "json"
```

Note that for this to work, your object must be JSON-serializable.

### Object Metadata

You can get metainfo (datetime and UUID) for a given object by passing `metainfo=True` to `load`, like so:

```python
# Load our object and metainfo!
user, datetime, uuid = nodb.load("Jeff", metainfo=True)
```

You can also pass in a `default` argument for non-existent values.

```python
user = nodb.load("Jeff", default={}) # {}
```

### Human Readable Indexes

By default, the indexes are hashed. If you want to be able to debug through the AWS console, set `human_readable_indexes` to True:

```python
nodb.human_readable_indexes = True
```

### Caching

You can enable local file caching, which will store previously retrieved values in the local rather than remote filestore.

```python
nodb.cache = True
```

### AWS settings override

You can override your AWS Profile information or boto3 session by passing either as a initial keyword argument.

```python
nodb = NoDB(profile_name='my_aws_development_profile')
# or supply the session
session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    aws_session_token=SESSION_TOKEN,
)
nodb = NoDB(session=session)
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
* Pseudo-locking
* Performance/load testing

## Related Projects

* [Zappa](https://github.com/Miserlou/Zappa) - Python's server-less framework!
* [K.E.V.](https://github.com/capless/kev) - a Python ORM for key-value stores based on Redis, S3, and a S3/Redis hybrid backend.
* [s3sqlite](https://github.com/Miserlou/zappa-django-utils#using-an-s3-backed-database-engine) - An S3-backed database engine for Django

## Contributing

This project is still young, so there is still plenty to be done. Contributions are more than welcome!

Please file tickets for discussion before submitting patches. Pull requests should target `master` and should leave NoDB in a "shippable" state if merged.

If you are adding a non-trivial amount of new code, please include a functioning test in your PR. For AWS calls, we use the `placebo` library, which you can learn to use [in their README](https://github.com/garnaat/placebo#usage-as-a-decorator). The test suite will be run by [Travis CI](https://travis-ci.org/Miserlou/NoDB) once you open a pull request.

Please include the GitHub issue or pull request URL that has discussion related to your changes as a comment in the code ([example](https://github.com/Miserlou/Zappa/blob/fae2925431b820eaedf088a632022e4120a29f89/zappa/zappa.py#L241-L243)). This greatly helps for project maintainability, as it allows us to trace back use cases and explain decision making.

## License

(C) Rich Jones 2017, MIT License.

<br />
<p align="center">
  <a href="https://gun.io"><img src="http://i.imgur.com/M7wJipR.png" alt="Made by Gun.io"/></a>
</p>
