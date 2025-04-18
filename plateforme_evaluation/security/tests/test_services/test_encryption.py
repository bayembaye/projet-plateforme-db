from django.test import TestCase
from security.services.encryption import CryptoService
import os

class CryptoServiceTest(TestCase):
    def setUp(self):
        self.service = CryptoService()
        self.test_data = b"Donnees tres secretes"
    
    def test_encrypt_decrypt(self):
        encrypted = self.service.encrypt_data(self.test_data)
        decrypted = self.service.decrypt_data(encrypted)
        self.assertEqual(decrypted, self.test_data)
    
    def test_file_encryption(self):
        test_file = 'test_file.txt'
        encrypted_file = 'test_file.enc'
        
        with open(test_file, 'wb') as f:
            f.write(self.test_data)
        
        self.service.encrypt_file(test_file, encrypted_file)
        self.service.decrypt_file(encrypted_file, 'decrypted.txt')
        
        with open('decrypted.txt', 'rb') as f:
            content = f.read()
        
        self.assertEqual(content, self.test_data)
        
        os.remove(test_file)
        os.remove(encrypted_file)
        os.remove('decrypted.txt')