import sys
import os
import unittest

from salttesting import TestCase

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),
        '..', '..', '..', 'srv', 'salt', '_modules'))
import snapper


class SnapperTestCase(TestCase):

    def test_snapshot_to_data(self):
        snapshot = [42, 1, 41, 1457006571,
                    0, 'Some description', '', {'userdata1': 'userval1'}]
        data = snapper._snapshot_to_data(snapshot)
        self.assertEqual(data['id'], 42)
        self.assertEqual(data['pre'], 41)
        self.assertEqual(data['type'], 'pre')
        self.assertEqual(data['user'], 'root')
        self.assertEqual(data['timestamp'], 1457006571)
        self.assertEqual(data['description'], 'Some description')
        self.assertEqual(data['cleanup'], '')
        self.assertEqual(data['userdata']['userdata1'], 'userval1')

if __name__ == '__main__':
    unittest.main()
