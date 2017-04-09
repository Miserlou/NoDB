# -*- coding: utf8 -*-
import base64
import collections
import json

import os
import random
import string
import zipfile
import re
import unittest
import shutil
import sys
import tempfile

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
        nodb = NoDB()

if __name__ == '__main__':
    unittest.main()
