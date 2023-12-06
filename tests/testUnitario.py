import unittest
from icedrive_blob.blob import BlobService
from pathlib import Path

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

if __name__ == '__main__':
    unittest.main()