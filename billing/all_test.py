import unittest

from test.db.test_cond import CondTestCase
from test.db.test_query_builder import QueryBuilderTestCase
from test.db.test_wrapper import WrapperTestCase

from test.install.test_install import InstallTestCase, DbPatchesTestCase
from test.mapping.test_actions import ActionsTestCase
from test.mapping.test_objects import PatchTestCase

if __name__ == '__main__':
    unittest.main()
