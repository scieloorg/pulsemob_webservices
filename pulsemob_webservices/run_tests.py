# coding: utf-8
import logging

__author__ = 'jociel'

import unittest
from tests import article_harvest_test


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(article_harvest_test.suite())
    return test_suite

if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    unittest.main(defaultTest='suite')
