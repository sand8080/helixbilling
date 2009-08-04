import unittest
from datetime import datetime

from mapping.objects import Patch

class PatchTestCase(unittest.TestCase):

    def test_creation(self):
        p = Patch(**{'id': 4})
        self.assertEqual(4, p.id)
        p = Patch(**{'id': 4, 'name': '1', 'path': 'path_to patch', 'date': datetime.now()})
        self.assertEqual(4, p.id)
        self.assertEqual('1', p.name)
        self.assertEqual('path_to patch', p.path)

    def test_creation_failure(self):
        self.assertRaises(TypeError, Patch, {'failure_attr': 1})

if __name__ == '__main__':
    unittest.main()
