import unittest

runner = unittest.TextTestRunner()

loader = unittest.TestLoader()
testsuite = loader.discover('.', pattern='test_*.py')
runner.run(testsuite)
