from icedrive_blob.blob import BlobService
from pathlib import Path
import json


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

'''
rutaFicheroJson = Path("pruebas").joinpath("enlaces.json") #obtener ruta absoluta del fichero de tipo de objeto Path

linked_blobs = {"pruebaLink":3, "id2":2}
with open(rutaFicheroJson, 'w') as f:
    json.dump(linked_blobs, f)
'''
b = BlobService("pruebas")
#b.link("pruebaLink")
blob = DataTransferDouble() # Crea un objeto simulado
blob_id = b.upload(blob) # Llama a la función upload
print(blob_id)
b.link("f2271c0f987c8a791fd0b63a64d3d2b86556f5c254fde953d07377462db5b6c0")

