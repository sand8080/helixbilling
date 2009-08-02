import unittest
import os

from install.install import filter_diapasone, filter_patches, filter_backward, filter_forward
from install.install import get_patches

class InstallTestCase(unittest.TestCase):

    def test_filter_diapasone(self):
        self.assertTrue(filter_diapasone('1', '5', '4-6-7'))
        self.assertTrue(filter_diapasone('1', None, '5'))
        self.assertTrue(filter_diapasone(None, '7', '5'))
        self.assertTrue(filter_diapasone('4', '7', '5'))
        self.assertFalse(filter_diapasone('4', '7', '2-3'))
        self.assertFalse(filter_diapasone('4', None, '2-3'))
        self.assertFalse(filter_diapasone(None, '2', '2-3'))

    def test_filter_patches(self):
        patches = ['1', '2-2', '37', '4', '4-1', '4-1-0', '35', '35-0']
        self.assertEqual(
            ['2-2', '4', '4-1', '4-1-0', '35', '35-0', '37'],
            filter_patches('2', '7-9-1', patches, reverse=False)
        )
        self.assertEqual(
            ['1', '2-2', '4', '4-1', '4-1-0', '35', '35-0', '37'],
            filter_patches(None, '7-9-1', patches, reverse=False)
        )
        self.assertEqual(
            ['37', '35-0', '35', '4-1-0', '4-1', '4', '2-2', '1'],
            filter_patches(None, '7-9-1', patches, reverse=True)
        )

    def test_filter_backward(self):
        patches = ['1', '2-2', '3', '7-9-9', '6']
        self.assertEqual(
            ['7-9-9', '6', '3', '2-2', '1'],
            filter_backward(None, None, patches)
        )

    def test_get_patches(self):
        patches = get_patches(os.path.join(
            os.path.realpath(os.path.dirname(__file__)),
            'patches'
        ))
        self.assertEqual(
            ['1', '1-1', '4', '37'],
            filter_forward(None, None, patches)
        )

if __name__ == '__main__':
    unittest.main()