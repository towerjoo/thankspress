#!/venv/bin/python
import unittest

if __name__ == '__main__':
    from app.user.test import TestCase as UserTestCase
    from app.thank.test import TestCase as ThankTestCase
    unittest.main(verbosity=2)