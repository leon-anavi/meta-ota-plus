'''
Tests for ostree_image tool
'''

from unittest import TestCase
from textwrap import dedent

from ostree_image import UpdateMetaData, OtaPlusUpdate

class BasicTest(TestCase):
    def test_example(self):
        self.assertEqual(1, 1)


class UpdateMetaDataTest(TestCase):
    def test_simple(self):
        c = UpdateMetaData()
        c.config_package = 'bob'
        c.config_delta_to = 'asdfasdfas'
        c.config_version = '1.0'
        res = c.write_out()
        golden = '''\
        CONFIG_PACKAGE=bob
        CONFIG_VERSION=1.0
        CONFIG_DELTA_TO=asdfasdfas
        CONFIG_PATH=/
        CONFIG_UNION=True
        CONFIG_DELTA_FROM=
        '''
        self.assertEqual(dedent(golden), res)

class OtaPlusUpdateTest(TestCase):
    def test_parse(self):
        fn = 'minimal-delta0-empty-f9fec916c2b05805f22ced2564a0bf6a2f7bc253b242d5bbbb103d7b9f4a6ea1.tar.gz'
        o = OtaPlusUpdate.parse_from_filename('minimal', fn)
        golden = OtaPlusUpdate(0, 'empty', 'f9fec916c2b05805f22ced2564a0bf6a2f7bc253b242d5bbbb103d7b9f4a6ea1')
        self.assertEqual(o, golden)
    def test_order(self):
        f1 = 'minimal-delta0-empty-f9fec916c2b05805f22ced2564a0bf6a2f7bc253b242d5bbbb103d7b9f4a6ea1.tar.gz'
        f2 = 'minimal-delta2-069c6c7081016aeb05c173e3613cd2531527811eaa5c8e6a5a12eaedbaba1a72-54e1e11ddbf33782f0cdc063cc18f22af5cb9d5f3ac0aa12f7dd06c597359636.tar.gz'
        a1 = OtaPlusUpdate.parse_from_filename('minimal', f1)
        a2 = OtaPlusUpdate.parse_from_filename('minimal', f2)
        self.assertTrue(a1.is_earlier_than(a2))
        self.assertFalse(a2.is_earlier_than(a1))
