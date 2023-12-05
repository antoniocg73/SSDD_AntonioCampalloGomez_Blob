"""Module for servants implementations."""

import Ice

import IceDrive 
import hashlib
import os
import json
from pathlib import Path

class DataTransfer(IceDrive.DataTransfer): #DUDA DE SI ES SOLO UN FICHERO
    """Implementation of an IceDrive.DataTransfer interface."""

    def __init__(self, source):
        # Si source es una cadena, asumimos que es la ruta a un archivo en disco
        #self.source_type = "file" # Almacena el tipo de fuente
        self.file_path = source # Almacena la ruta al archivo
        self.file = open(self.file_path, 'rb') # Abre el archivo en modo lectura binaria
    

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file or blob_data."""
        data = self.file.read(size) # Lee size bytes del archivo
        return data

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        if not self.file.closed: # Si no está cerrado
            self.file.close() # Se cierra el archivo
            current.adapter.remove(current.id) #revisar si es current.id  # Se elimina el objeto DataTransfer del adaptador
                        
class BlobService(IceDrive.BlobService): 
    """Implementation of an IceDrive.BlobService interface."""

    #SI
    def __init__(self, directory_path):
        self.directory_path = directory_path # Almacena la ruta al directorio   
        self.rutaFicheroJson = Path(directory_path).joinpath("enlaces.json") #obtener ruta absoluta del fichero de tipo de objeto Path
        if not os.path.exists(self.rutaFicheroJson): #si no existe el fichero
            self.escribirEnJson()
            self.linked_blobs = {} # Diccionario de blobs vinculados
        else:
            self.leerDeJson()

    def _get_blob_data(self, blob: IceDrive.DataTransferPrx, current: Ice.Current) -> bytes:
        """Lee los datos del blob."""
        data_transfer = blob # Obtiene el proxy del objeto DataTransfer
        blob_data = bytearray() # Inicializa un array de bytes para almacenar los datos del blob
        while True: # Mientras haya datos
            chunk = data_transfer.read(4096) # Lee 4096 bytes del blob
            if not chunk: # Si no hay datos, se cierra el fichero
                break # Se cierra el fichero 
            blob_data += chunk # Añade los datos leídos al array de bytes
            #Ir guardando trocitos en un fichero temporal y que esto me devuelva la ruta al fichero temporal
            #tmpfile = tempfile.NamedTemporaryFile(delete=False)

        return blob_data # Devuelve los datos del blob
    
    #funcion para calcular el hash de los datos del blob ya existentes en el directorio
    #json para persistencia para recordar los enlaces a archivos, los links

    #BLOB SERVICE: ALMACENADO LA RELACION ENTRE EL BLOB ID Y LA RUTA DEL FICHERO
    #OTRA RELACION EL BLOB ID TIENE 1 RELACION DE ENLACES, SOLO 1 RELACION DE ENLACES
    # json clave blob_id valor numero de enlaces del blob_id




    #Recomendacion: otra clase para la gestion de los ficheros

    def _generate_blob_id(self, blob_data: bytes) -> str:
        """Genera un identificador de blob basado en los datos."""
        return str(hash(blob_data)) # Devuelve el hash de los datos del blob

    def _create_data_transfer(self, blob_data: bytes, current: Ice.Current) -> IceDrive.DataTransferPrx:
        """Crea un objeto DataTransfer y devuelve su proxy."""
        data_transfer_impl = DataTransfer(blob_data) # Crea un objeto DataTransfer
        data_transfer_proxy = current.adapter.addWithUUID(data_transfer_impl) # Obtiene el proxy del objeto DataTransfer
        return IceDrive.DataTransferPrx.uncheckedCast(data_transfer_proxy) # Devuelve el proxy del objeto DataTransfer


    #SI
    def escribirEnJson(self):
        with open(self.rutaFicheroJson, 'w') as f:
            json.dump(self.linked_blobs, f)
    #SI
    def leerDeJson(self):
        with open(self.rutaFicheroJson, 'r') as f:
            self.linked_blobs = json.load(f)
    #SI
    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        if blob_id in self.linked_blobs: # Si el blob está almacenado 
            self.linked_blobs[blob_id] += 1 # Se marca como vinculado
            self.escribirEnJson()
        else:
            raise IceDrive.UnknownBlob(blob_id) # Si no está almacenado, se lanza una excepción
    #SI
    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        if blob_id in self.linked_blobs: # Si el blob está almacenado
                self.linked_blobs[blob_id] -=1 # Se marca como no vinculado 
                if self.linked_blobs[blob_id] == 0: # Si el blob no está vinculado
                    del self.linked_blobs[blob_id] # Se elimina del diccionario de blobs vinculados
                    rutaFicheroAEliminar = Path(self.directory_path).joinpath(blob_id) #obtener ruta absoluta del fichero
                    os.unlink(rutaFicheroAEliminar) #borrar fichero del disco
                self.escribirEnJson()
        else:
            raise IceDrive.UnknownBlob("Blob no encontrado") # Si no está almacenado, se lanza una excepción

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str:
        """Register a DataTransfer object to upload a file to the service."""
        #Cuando me mandan el blob, hacer bucle hacendo reads en un archivo temporal e ir escribiendo en mi archivo normal hasta recibirlo entero (devuelve cadena vacía) 
        # y luego cerrar el archivo temporal 
        #libreria archivos temporales de python tempfile
        # le tengo q decir q no borre el archivo temporal delete_on_close=False
        #todo esto en get_blob_data
        try:
            blob_data = self._get_blob_data(blob, current) # Obtiene los datos del blob
            blob_id = self._generate_blob_id(blob_data) # Genera un identificador para el blob
            self.blob_storage[blob_id] = blob_data # Almacena el blob
            self.linked_blobs[blob_id] = False # Marca el blob como no vinculado
            return blob_id # Devuelve el identificador del blob
        except Exception as e:
            raise IceDrive.FailedToReadData(str(e)) # Si no se pueden leer los datos, se lanza una excepción

    def download(
        self, blob_id: str, current: Ice.Current = None
    ) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        if blob_id in self.blob_storage: # Si el blob está almacenado
            blob_data = self.blob_storage[blob_id] # Obtiene los datos del blob
            return self._create_data_transfer(blob_data, current) # Crea un objeto DataTransfer
        else:
            raise IceDrive.UnknownBlob("Blob no encontrado") # Si no está almacenado, se lanza una excepción
        
        #Crear dicrectorio al mismo nivel de icedrive_blob para pruebas unitarias