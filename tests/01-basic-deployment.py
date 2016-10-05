#!/usr/bin/env python3

import unittest
import amulet


class TestDeploy(unittest.TestCase):
    """
    Trivial deployment test for the Apache Bigtop compute slave.

    This is used as a base layer for building the hadoop-slave charm.
    It cannot do anything useful by itself, so integration testing
    is done in the hadoop-processing bundle.
    """

    def test_deploy(self):
        self.d = amulet.Deployment(series='xenial')
        self.d.add('slave', 'hadoop-slave')
        self.d.setup(timeout=900)
        self.d.sentry.wait(timeout=1800)
        self.unit = self.d.sentry['slave'][0]


if __name__ == '__main__':
    unittest.main()
