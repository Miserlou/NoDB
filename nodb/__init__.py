from datetime import datetime
from io import BytesIO

import boto3
import botocore
import hashlib
import json
import uuid
import six

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

    s3 = boto3.resource('s3', config=botocore.client.Config(signature_version=signature_version))

    ##
    # Advanced config
    ##
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

        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def load(self, index, metainfo=False):
        """
        Load an object from the backend datastore.

        Returns None if not found.
        """

        # First, calculate the real index
        real_index = self._format_index_value(index)

        # Next, get the bytes (if any)
        try:
            serialized_s3 = self.s3.Object(self.bucket, self.prefix + real_index)
            serialized = serialized_s3.get()["Body"].read()
        except botocore.exceptions.ClientError:
            # No Key? Return None.
            return None

        # Then read the data format
        deserialized = self._deserialize(serialized)

        # And return the data
        if metainfo:
            return deserialized['obj'], (deserialized['dt'], deserialized['uuid'])
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
        packed['obj'] = obj

        if self.serializer == 'pickle':
            serialized = pickle.dumps(packed)
        elif self.serializer == 'json':
            serialized = json.dumps(packed).encode('utf-8')
        else:
            raise Exception("Unsupported serialize format: " + str(self.serializer))

        return six.binary_type(serialized)

    def _deserialize(self, serialized):
        """
        Unpack and load data from a serialized NoDB entry.
        """
        if self.serializer == 'pickle':
            deserialized = pickle.loads(serialized)
        elif self.serializer == 'json':
            deserialized = json.loads(serialized.decode('utf-8'))
        else:
            raise Exception("Unsupported serializer format set on initialization")

        return deserialized


    def _get_object_index(self, obj, index):
        """
        Get the "Index" value for this object. This may be a hashed index.

        If it's a dictionary, get the key.
        If it has that as an attribute, get that attribute as a string.
        If it doesn't have an attribute, or has an illegal attribute, fail.
        """

        if type(obj) is dict:
            if index in obj:
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

        if self.human_readable_indexes:
            # You are on your own here! This may not work!
            return index_value
        else:
            return self.hash_function(six.binary_type(index_value.encode('utf-8'))).hexdigest()
