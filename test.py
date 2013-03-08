#!venv/bin/python
import unittest

if __name__ == '__main__':
    from app.email.test import TestCase as EmailTestCase
    from app.thank.test import TestCase as ThankTestCase
    from app.user.test import TestCase as UserTestCase
    unittest.main(verbosity=2)