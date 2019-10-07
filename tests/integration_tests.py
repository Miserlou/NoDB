# -*- coding: utf8 -*-
import random
import string
import unittest
from nodb import NoDB


class TestNoDBIntegration(unittest.TestCase):

    def test_nodb_save_load_all_subpath(self):
        bucket_name = 'noahonnumbers-blog'

        nodb = NoDB(bucket_name)
        nodb.human_readable_indexes = True
        nodb.index = "path"

        jeff = {"Name": "Jeff", "age": 19, "path": "persons/jeff", "type": "person"}
        michael = {"Name": "Michael", "age": 19, "path": "persons/michael", "type": "person"}
        car = {"Name": "Acura TSX", "path": "vehicles/car", "type": "vehicle"}

        nodb.save(jeff)
        nodb.save(michael)
        nodb.save(car)

        persons = nodb.all(subpath="persons/")
        self.assertListEqual([jeff, michael], persons)


if __name__ == '__main__':
    unittest.main()
