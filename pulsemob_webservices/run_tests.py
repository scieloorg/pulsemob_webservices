import unittest

__author__ = 'jociel'

from tests import article_harvest_test


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(article_harvest_test.suite())
    return test_suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
