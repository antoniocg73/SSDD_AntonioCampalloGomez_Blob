import unittest
from unittest.mock import Mock
import Ice
import IceDrive 
from icedrive_blob.blob import BlobService
from pathlib import Path
import os
class TestBlobService(unittest.TestCase):
    def setUp(self):
        self.b = BlobService("pruebas")

    def test_link(self):
        self.b.link("pruebaLink")
        self.assertIn("pruebaLink", self.b.linked_blobs)

    def test_unlink(self):
        #self.b.link("pruebaLink")
        self.b.unlink("pruebaLink")
        self.assertIn("pruebaLink", self.b.linked_blobs)

    def test_upload(self):
        blob = IceDrive.DataTransferPrx() # Crea un objeto simulado
        blob.read = Mock(return_value=b"test data") # Simula el método read
        blob.close = Mock() # Simula el método close
        blob_id = self.b.upload(blob) # Llama a la función upload
        self.assertIn(blob_id, self.b.linked_blobs) # Verifica que el blob_id está en linked_blobs
        blob_path = Path(self.b.directory_path).joinpath(blob_id) # Calcula la ruta del archivo
        self.assertTrue(os.path.exists(blob_path.name)) # Verifica que el archivo existe

if __name__ == '__main__':
    unittest.main()