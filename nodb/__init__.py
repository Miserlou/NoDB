from datetime import datetime
from io import BytesIO

import base64
import boto3
import botocore
import hashlib
import json
import logging
import os
import tempfile
import uuid

try:
    import cPickle as pickle
except Exception:
    import pickle

class NoDB(object):
    """
    A NoDB connection object.
    """

    ##
    # Config
    ##

    bucket = None
    backend = "s3"
    region = "us-east-1"
    serializer = "pickle"
    index = "id"
    prefix = ".nodb/"
    signature_version = "s3v4"
    cache = False

    s3 = boto3.resource('s3', config=botocore.client.Config(signature_version=signature_version))

    ##
    # Advanced config
    ##

    cache_dir = tempfile.gettempdir()
    human_readable_indexes = False
    hash_function = hashlib.sha256

    ##
    # Public Interfaces
    ##

    def save(self, obj, index=None):
        """
        Save an object to the backend datastore.

        Will use this NoDB's index by default if an explicit index isn't supplied.
        """

        # First, serialize.
        serialized = self._serialize(obj)

        # Next, compute the index
        if not index:
            real_index = self._get_object_index(obj, self.index)
        else:
            real_index = self._format_index_value(index)

        # Then, store.
        bytesIO = BytesIO()
        bytesIO.write(serialized)
        bytesIO.seek(0)

        s3_object = self.s3.Object(self.bucket, self.prefix + real_index)
        result = s3_object.put('rb', Body=bytesIO)
        logging.debug("Put remote bytes: " + self.prefix + real_index)

        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            resp = True
        else:
            resp = False

        # If cache enabled, write this value to cache.
        if resp and self.cache:

            base_cache_path = self._get_base_cache_path()
            cache_path = os.path.join(base_cache_path, real_index)
            if not os.path.exists(cache_path):
                open(cache_path, 'w+').close()
            with open(cache_path, "wb") as in_file:
                in_file.write(serialized)
            logging.debug("Wrote to cache file: " + cache_path)

        return resp

    def load(self, index, metainfo=False, default=None):
        """
        Load an object from the backend datastore.

        Returns None if not found.
        """

        # First, calculate the real index
        real_index = self._format_index_value(index)

        # If cache enabled, check local filestore for bytes
        cache_hit = False
        if self.cache:
            base_cache_path = self._get_base_cache_path()
            cache_path = os.path.join(base_cache_path, real_index)
            # Cache hit!
            if os.path.isfile(cache_path):
                with open(cache_path, "rb") as in_file:
                    serialized = in_file.read()
                cache_hit = True
                logging.debug("Loaded bytes from cache file: " + cache_path)
            else:
                cache_hit = False

        # Next, get the bytes (if any)
        if not self.cache or not cache_hit:
            try:
                serialized_s3 = self.s3.Object(self.bucket, self.prefix + real_index)
                serialized = serialized_s3.get()["Body"].read()
            except botocore.exceptions.ClientError as e:
                # No Key? Return default.
                logging.debug("No remote object, returning default.")
                return default

            # Store the cache result
            if self.cache:

                if not os.path.exists(cache_path):
                    open(cache_path, 'w+').close()

                with open(cache_path, "wb") as in_file:
                    in_file.write(serialized)

                logging.debug("Wrote to cache file: " + cache_path)

        # Then read the data format
        deserialized = self._deserialize(serialized)

        # And return the data
        if metainfo:
            return deserialized['obj'], (
                                            deserialized['dt'],
                                            deserialized['uuid']
                                        )
        else:
            return deserialized['obj']

    def delete(self, index):
        """
        Given an index, delete this object.
        """

        # First, calculate the real index
        real_index = self._format_index_value(index)

        # Next, get the bytes (if any)
        serialized_s3 = self.s3.Object(self.bucket, self.prefix + real_index)
        result = serialized_s3.delete()

        if result['ResponseMetadata']['HTTPStatusCode'] in [200, 204]:
            return True
        else:
            return False


    ###
    # Private interfaces
    ###

    def _serialize(self, obj):
        """
        Create a NoDB storage item. They exist in the format:

        /my_bucket/_nodb/[[index]]
        {
            "serializer:" [[serializer_format]],
            "dt": [[datetime created]],
            "uuid": [[uuid4]],
            "obj": [[object being saved]]
        }

        """

        packed = {}
        packed['serializer'] = self.serializer
        packed['dt'] = str(datetime.utcnow())
        packed['uuid'] = str(uuid.uuid4())

        if self.serializer == 'pickle':
            # TODO: Python3
            packed['obj'] = str(base64.b64encode(pickle.dumps(obj)))
        elif self.serializer == 'json':
            packed['obj'] = obj
        else:
            raise Exception("Unsupported serialize format: " + str(self.serializer))

        return json.dumps(packed)

    def _deserialize(self, serialized):
        """
        Unpack and load data from a serialized NoDB entry.
        """

        obj = None
        deserialized = json.loads(serialized)
        return_me = {}

        if deserialized['serializer'] == 'pickle':

            if self.serializer != 'pickle':
                raise Exception("Security exception: Won't unpickle if not set to pickle.")

            # TODO: Python3
            return_me['obj'] = pickle.loads(base64.b64decode(deserialized['obj']))

        elif deserialized['serializer'] == 'json':
            return_me['obj'] = deserialized['obj']

        else:
            raise Exception("Unsupported serialize format: " + deserialized['serializer'])

        return_me['dt'] = deserialized['dt']
        return_me['uuid'] = deserialized['uuid']

        return return_me

    def _get_object_index(self, obj, index):
        """
        Get the "Index" value for this object. This may be a hashed index.

        If it's a dictionary, get the key.
        If it has that as an attribute, get that attribute as a string.
        If it doesn't have an attribute, or has an illegal attribute, fail.
        """

        index_value = None
        if type(obj) is dict:
            if obj.has_key(index):
                index_value = obj[index]
            else:
                raise Exception("Dict object has no key: " + str(index))
        else:
            if hasattr(obj, index):
                index_value = getattr(obj, index)
            else:
                raise Exception("Dict object has no attribute: " + str(index))

        return self._format_index_value(index_value)

    def _format_index_value(self, index_value):
        """
        Hash these bytes, or don't.
        """

        logging.debug("Formatting index value: " + str(index_value))

        if self.human_readable_indexes:
            # You are on your own here! This may not work!
            return index_value
        else:
            return self.hash_function(bytes(index_value)).hexdigest()

    def _get_base_cache_path(self):
        """
        Make sure that the cache directory is real. Returns the path.
        """

        base_cache_path = os.path.join(self.cache_dir, '.nodb')
        if not os.path.isdir(base_cache_path):
            os.makedirs(base_cache_path)
        return base_cache_path
