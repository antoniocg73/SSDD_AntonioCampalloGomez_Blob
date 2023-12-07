import unittest
from icedrive_blob.blob import BlobService
from pathlib import Path
import os
import Ice
Ice.loadSlice("icedrive_blob/icedrive.ice")
import IceDrive 

class DataTransferDouble:
    def __init__(self):
        self.output = "Hello world\n"
        self.index = -1
    def read(self, size):
        self.index += 1
        if self.index >= len(self.output) - 1:
            return b""
        return self.output[self.index].encode()

    def close(self):
        pass

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
        blob = DataTransferDouble() # Crea un objeto simulado
        blob_id = self.b.upload(blob) # Llama a la función upload
        self.assertIn(blob_id, self.b.linked_blobs) # Verifica que el blob_id está en linked_blobs
        blob_path = Path(self.b.directory_path).joinpath(blob_id) # Calcula la ruta del archivo
        self.assertTrue(os.path.exists(blob_path.name)) # Verifica que el archivo existe

if __name__ == '__main__':
    unittest.main()