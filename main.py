from icedrive_blob.blob import BlobService
from pathlib import Path
import json

rutaFicheroJson = Path("pruebas").joinpath("enlaces.json") #obtener ruta absoluta del fichero de tipo de objeto Path

linked_blobs = {"pruebaLink":3, "id2":2}
with open(rutaFicheroJson, 'w') as f:
    json.dump(linked_blobs, f)

b = BlobService("pruebas")
#b.link("pruebaLink")
b.link("id2")

