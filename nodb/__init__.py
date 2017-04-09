from datetime import datetime
from io import BytesIO

import base64
import boto3
import hashlib
import json
import uuid

try:
    import cPickle as pickle
except Exception:
    import pickle

s3 = boto3.resource('s3')

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

    ##
    # Advanced config
    ##
    human_readable_indexes = False
    hash_function = hashlib.sha256

    ##
    # Public Interfaces
    ##

    def save(self, obj):
        """
        Save an object to the backend datastore.
        """

        # First, serialize.
        serialized = self._serialize(obj)

        # Next, compute the index
        real_index = self._get_object_index(obj, self.index)

        # Then, store.
        bytesIO = BytesIO()
        bytesIO.write(serialized)
        bytesIO.seek(0)


        s3_object = s3.Object(self.bucket, self.prefix + real_index)
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
        serialized_s3 = s3.Object(self.bucket, self.prefix + real_index)
        serialized = serialized_s3.get()["Body"].read()

        # No record, return None.
        if not serialized:
            return None

        # Then read the data format
        deserialized = self._deserialize(serialized)

        # And return the data
        if metainfo:
            return deserialized['obj'], (deserialized['dt'], deserialized['uuid'])
        else:
            return deserialized['obj']

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
                index_value = obj.index
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
            return self.hash_function(bytes(index_value)).hexdigest()
