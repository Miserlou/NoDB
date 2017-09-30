# -*- coding: utf8 -*-
import base64
import collections
import json

import os
import random
import string
import zipfile
import re
import shutil
import sys
import tempfile
import unittest

import boto3
import moto

from nodb import NoDB

def random_string(length):
    return ''.join(random.choice(string.printable) for _ in range(length))

class TestNoDB(unittest.TestCase):
    # def setUp(self):
    #     self.sleep_patch = mock.patch('time.sleep', return_value=None)
    #     # Tests expect us-east-1.
    #     # If the user has set a different region in env variables, we set it aside for now and use us-east-1
    #     self.users_current_region_name = os.environ.get('AWS_DEFAULT_REGION', None)
    #     os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    #     if not os.environ.get('PLACEBO_MODE') == 'record':
    #         self.sleep_patch.start()

    # def tearDown(self):
    #     if not os.environ.get('PLACEBO_MODE') == 'record':
    #         self.sleep_patch.stop()
    #     del os.environ['AWS_DEFAULT_REGION']
    #     if self.users_current_region_name is not None:
    #         # Give the user their AWS region back, we're done testing with us-east-1.
    #         os.environ['AWS_DEFAULT_REGION'] = self.users_current_region_name

    ##
    # Sanity Tests
    ##

    def test_test(self):
        self.assertTrue(True)
    ##
    # Basic Tests
    ##

    def test_nodb(self):
        self.assertTrue(True)
        nodb = NoDB('dummy')
        nodb.index = "Name"

        jeff = {"Name": "Jeff", "age": 19}
        serialized = nodb._serialize(jeff)
        nodb._deserialize(serialized)

        nodb.serializer = 'json'
        nodb.human_readable_indexes = True
        serialized = nodb._serialize(jeff)
        nodb._deserialize(serialized)

    @moto.mock_s3
    def test_nodb_save_load(self):
        self.assertTrue(True)
        # create dummy bucket and store some objects
        bucket_name = 'dummy_bucket'
        boto3.resource('s3').Bucket(bucket_name).create()

        nodb = NoDB(bucket_name)
        nodb.index = "Name"

        jeff = {"Name": "Jeff", "age": 19}

        nodb.save(jeff)
        possible_jeff = nodb.load('Jeff')
        self.assertEqual(possible_jeff, jeff)

    def test_nodb_cache(self):
        self.assertTrue(True)
        nodb = NoDB('dummy')
        nodb.index = "Name"
        nodb.cache = True

        jeff = {"Name": "Jeff", "age": 19}
        serialized = nodb._serialize(jeff)

        real_index = nodb._format_index_value("Jeff")
        base_cache_path = os.path.join(tempfile.gettempdir(), '.nodb')
        if not os.path.isdir(base_cache_path):
            os.makedirs(base_cache_path)

        cache_path = os.path.join(base_cache_path, real_index)
        if not os.path.exists(cache_path):
            f = open(cache_path, 'a')
            f.close()

        with open(cache_path, "wb") as in_file:
            in_file.write(serialized)

        nodb.load("Jeff")
        loaded = nodb.load("Jeff", default={})
        self.assertEqual(loaded, jeff)
        loaded = nodb.load("Jeff", default="Booty")
        self.assertEqual(loaded, jeff)

        bcp = nodb._get_base_cache_path()

    @moto.mock_s3()
    def test_nodb_all(self):
        # create dummy bucket and store some objects
        bucket_name = 'dummy_bucket'
        boto3.resource('s3').Bucket(bucket_name).create()

        nodb = NoDB(bucket_name)
        nodb.index = "Name"

        nodb.save({"Name": "John", "age": 19})
        nodb.save({"Name": "Jane", "age": 20})

        all_objects = nodb.all()
        self.assertListEqual([{"Name": "John", "age": 19}, {"Name": "Jane", "age": 20}], all_objects)


if __name__ == '__main__':
    unittest.main()
