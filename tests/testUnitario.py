import unittest
from icedrive_blob.blob import BlobService
from pathlib import Path
import os
import Ice
import json
import hashlib
Ice.loadSlice("icedrive_blob/icedrive.ice")

#tests sin Ice aplicado, comentar lineas de download para que funcionen
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
        rutaFicheroJson = Path("pruebas").joinpath("enlaces.json") #obtener ruta absoluta del fichero de tipo de objeto Path
        linked_blobs = {"pruebaLink":3, "id2":2}
        with open(rutaFicheroJson, 'w') as f:
            json.dump(linked_blobs, f)
        self.b = BlobService("pruebas")

    def calculate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

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
        self.assertTrue(os.path.exists(blob_path)) # Verifica que el archivo existe

    def test_download(self):
        blob = DataTransferDouble()  # Crea un objeto simulado
        blob_id = self.b.upload(blob)  # Llama a la función upload
        downloaded_blob = self.b.download(blob_id)  # Llama a la función download
        self.assertEqual(blob_id, downloaded_blob.blob_id )  # Verifica que los datos son iguales
    
    def test_link_unlink(self):
        # Crea un objeto simulado
        blob = DataTransferDouble()
        # Llama a la función upload
        blob_id = self.b.upload(blob)
        # Llama a la función link
        self.b.link(blob_id)
        # Verifica que el blob_id está en linked_blobs
        self.assertIn(blob_id, self.b.linked_blobs)
        # Llama a la función unlink
        self.b.unlink(blob_id)
        # Verifica que el blob_id ya no está en linked_blobs
        self.assertNotIn(blob_id, self.b.linked_blobs)

    def test_upload_unlink(self):
        blob = DataTransferDouble() # Crea un objeto simulado
        blob_id = self.b.upload(blob) # Llama a la función upload
        self.assertIn(blob_id, self.b.linked_blobs) # Verifica que el blob_id está en linked_blobs
        self.b.unlink(blob_id) # Llama a la función unlink
        self.assertNotIn(blob_id, self.b.linked_blobs) # Verifica que el blob_id ya no está en linked_blobs
    
    def test_sha256(self):
        downloaded_blob = self.b.download("pruebaLink")  # Llama a la función download
        file_path_origin = Path(self.b.directory_path).joinpath("pruebaLink")
        hash_origin = self.calculate_hash(file_path_origin)
        hash_downloaded = self.calculate_hash(downloaded_blob.file_path)
        self.assertEqual(hash_origin, hash_downloaded)

if __name__ == '__main__':
    unittest.main()