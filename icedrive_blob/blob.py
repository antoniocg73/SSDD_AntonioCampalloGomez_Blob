"""Module for servants implementations."""

import Ice

import IceDrive 
import hashlib


class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""

    def __init__(self, source):
        if isinstance(source, str):
            # Si source es una cadena, asumimos que es la ruta a un archivo en disco
            self.source_type = "file" # Almacena el tipo de fuente
            self.file_path = source # Almacena la ruta al archivo
            self.file = open(self.file_path, 'rb') # Abre el archivo en modo lectura binaria
        else:
            # Si source no es una cadena, asumimos que son los propios datos del blob
            self.source_type = "blob_data" # Almacena el tipo de fuente
            self.blob_data = source # Almacena los datos del blob
            self.position = 0 # Almacena la posición actual en los datos del blob

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file or blob_data."""
        if self.source_type == "file": # Si la fuente es un archivo
            data = self.file.read(size) # Lee size bytes del archivo
            if not data: # Si no hay datos
                self.close(current) # Se cierra el archivo
        else:
            data = self.blob_data[self.position : self.position + size] # Lee size bytes de los datos del blob
            self.position += size # Actualiza la posición actual en los datos del blob
        return data

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        if self.source_type == "file" and not self.file.closed: # Si la fuente es un archivo y no está cerrado
            self.file.close() # Se cierra el archivo
            
class BlobService(IceDrive.BlobService): 
    """Implementation of an IceDrive.BlobService interface."""

    def __init__(self):
        self.blob_storage = {} # Inicializa un diccionario para almacenar blobs con sus identificadores
        self.linked_blobs = {} # Inicializa un diccionario para rastrear qué blobs están vinculados a directorios

    def _get_blob_data(self, blob: IceDrive.DataTransferPrx, current: Ice.Current) -> bytes:
        """Lee los datos del blob."""
        data_transfer = blob.ice_twoway().ice_timeout(-1) # Obtiene el proxy del objeto DataTransfer
        blob_data = bytearray() # Inicializa un array de bytes para almacenar los datos del blob
        while True: # Mientras haya datos
            chunk = data_transfer.read(4096, current) # Lee 4096 bytes del blob
            if not chunk: # Si no hay datos, se cierra el fichero
                break # Se cierra el fichero
            blob_data += chunk # Añade los datos leídos al array de bytes
        return bytes(blob_data) # Devuelve los datos del blob

    def _generate_blob_id(self, blob_data: bytes) -> str:
        """Genera un identificador de blob basado en los datos."""
        return str(hash(blob_data)) # Devuelve el hash de los datos del blob

    def _create_data_transfer(self, blob_data: bytes, current: Ice.Current) -> IceDrive.DataTransferPrx:
        """Crea un objeto DataTransfer y devuelve su proxy."""
        data_transfer_impl = DataTransfer(blob_data) # Crea un objeto DataTransfer
        data_transfer_proxy = current.adapter.addWithUUID(data_transfer_impl) # Obtiene el proxy del objeto DataTransfer
        return IceDrive.DataTransferPrx.uncheckedCast(data_transfer_proxy) # Devuelve el proxy del objeto DataTransfer


    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        if blob_id in self.blob_storage: # Si el blob está almacenado
            self.linked_blobs[blob_id] = True # Se marca como vinculado
        else:
            raise IceDrive.UnknownBlob("Blob no encontrado") # Si no está almacenado, se lanza una excepción
        
    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        if blob_id in self.blob_storage: # Si el blob está almacenado
                del self.linked_blobs[blob_id] # Se marca como no vinculado
                if blob_id not in self.linked_blobs: # Si el blob no está vinculado
                    del self.blob_storage[blob_id] # Se elimina del almacenamiento
        else:
            raise IceDrive.UnknownBlob("Blob no encontrado") # Si no está almacenado, se lanza una excepción

    def upload(
        self, blob: IceDrive.DataTransferPrx, current: Ice.Current = None
    ) -> str: #Me falta poner la excepción
        """Register a DataTransfer object to upload a file to the service."""
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