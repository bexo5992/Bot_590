# tests/test_basic.py
import unittest
from bot.utils.security import generate_link_code, generate_secure_code

class TestSecurity(unittest.TestCase):
    def test_generate_link_code(self):
        code = generate_link_code()
        self.assertEqual(len(code), 8)
        self.assertTrue(code.isalnum())
    
    def test_generate_secure_code(self):
        code = generate_secure_code()
        self.assertTrue(len(code) >= 16)

if __name__ == '__main__':
    unittest.main()
