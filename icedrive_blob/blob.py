"""Module for servants implementations."""

import Ice
import IceDrive 
import shutil
import os
import json
import hashlib
from pathlib import Path
import tempfile
from .discovery import Discovery

class DataTransfer(IceDrive.DataTransfer):
    """Implementation of an IceDrive.DataTransfer interface."""

    def __init__(self, source):
        # Si source es una cadena, asumimos que es la ruta a un archivo en disco
        #self.source_type = "file" # Almacena el tipo de fuente
        self.file_path = source # Almacena la ruta al archivo
        self.file = open(self.file_path, 'rb') # Abre el archivo en modo lectura binaria
        self.blob_id = os.path.basename(source)
    

    def read(self, size: int, current: Ice.Current = None) -> bytes:
        """Returns a list of bytes from the opened file or blob_data."""
        try:
            data = self.file.read(size) # Lee size bytes del archivo
            return data
        except Exception: # Si se produce un error
            raise IceDrive.FailedToReadData() # Si no se pueden leer los datos, se lanza una excepción

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        if not self.file.closed: # Si no está cerrado
            self.file.close() # Se cierra el archivo
            current.adapter.remove(current.id) # Se elimina el objeto DataTransfer del adaptador

class BlobService(IceDrive.BlobService): 
    """Implementation of an IceDrive.BlobService interface."""

    
    def __init__(self, directory_path, discovery: Discovery):
        self.directory_path = directory_path # Almacena la ruta al directorio   
        self.rutaFicheroJson = Path(directory_path).joinpath("enlaces.json") #obtener ruta absoluta del fichero de tipo de objeto Path
        self.discovery = discovery
        if not os.path.exists(self.rutaFicheroJson): #si no existe el fichero
            self.escribirEnJson()
            self.linked_blobs = {} # Diccionario de blobs vinculados
        else:
            self.leerDeJson()
    
    def escribirEnJson(self):
        with open(self.rutaFicheroJson, 'w') as f: #abrir fichero en modo escritura
            json.dump(self.linked_blobs, f) #guardar el diccionario de enlaces
    
    def leerDeJson(self):
        with open(self.rutaFicheroJson, 'r') as f: #abrir fichero en modo lectura
            self.linked_blobs = json.load(f) #cargar el diccionario de enlaces
    
    def link(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id file as linked in some directory."""
        if blob_id in self.linked_blobs: # Si el blob está almacenado 
            self.linked_blobs[blob_id] += 1 # Se marca como vinculado
            self.escribirEnJson()
        else:
            raise IceDrive.UnknownBlob(blob_id) # Si no está almacenado, se lanza una excepción
    
    def unlink(self, blob_id: str, current: Ice.Current = None) -> None:
        """Mark a blob_id as unlinked (removed) from some directory."""
        if blob_id in self.linked_blobs: # Si el blob está almacenado
             # Se marca como no vinculado 
            self.linked_blobs[blob_id] -=1
            if self.linked_blobs[blob_id] <= 0: # Si el blob no está vinculado
                del self.linked_blobs[blob_id] # Se elimina del diccionario de blobs vinculados
                rutaFicheroAEliminar = Path(self.directory_path).joinpath(blob_id) #obtener ruta absoluta del fichero
                os.unlink(rutaFicheroAEliminar) #borrar fichero del disco
            self.escribirEnJson()
        else:
            raise IceDrive.UnknownBlob(blob_id) # Si no está almacenado, se lanza una excepción

    def upload(self, user: IceDrive.UserPrx, blob: IceDrive.DataTransferPrx,  current: Ice.Current = None) -> str:
        """Register a DataTransfer object to upload a file to the service."""
        if self.discovery.getAuthentication().verifyUser(user): # Si el usuario está autenticado
            try:
                hash_object = hashlib.sha256() # Crea un objeto hash
                temp_file = tempfile.NamedTemporaryFile(delete=False) # Crea un fichero temporal
                while True:
                    data = blob.read(4096)
                    if not data:
                        blob.close()
                        break
                    hash_object.update(data) # Actualiza el hash con los datos leídos
                    temp_file.write(data) # Escribe los datos en el fichero
                blob_id = hash_object.hexdigest() # Devuelve el hash en formato hexadecimal
                if blob_id not in self.linked_blobs:
                    shutil.move(temp_file.name, Path(self.directory_path).joinpath(blob_id)) # Renombra el fichero temporal
                    self.linked_blobs.update({blob_id: 0}) # Añade el blob al diccionario de blobs vinculados
                    self.escribirEnJson()
                else:
                    #os.remove(temp_file)
                    print("It is already uploaded.") 
                return blob_id # Devuelve el hash del fichero
            
            except IceDrive.TemporaryUnavailable:
                raise IceDrive.TemporaryUnavailable()  # Manejar la excepción TemporaryUnavailable

            except Exception: # Si se produce un error
                raise IceDrive.FailedToReadData() # Si no se pueden leer los datos, se lanza una excepción
        else:
            print("User is not verified.")

    def download(self, user: IceDrive.UserPrx, blob_id: str, current: Ice.Current = None) -> IceDrive.DataTransferPrx:
        """Return a DataTransfer objet to enable the client to download the given blob_id."""
        if self.discovery.getAuthentication().verifyUser(user): # Si el usuario está autenticado
            try:
                if blob_id in self.linked_blobs: # Si el blob está almacenado
                    blob_path = Path(self.directory_path).joinpath(blob_id) #obtener ruta absoluta del fichero
                    if os.path.exists(blob_path): # Si el blob está almacenado
                        blob_transfer = DataTransfer(blob_path) # Crea un objeto DataTransfer
                        prx = current.adapter.addWithUUID(blob_transfer) # Añade el objeto DataTransfer al adaptador
                        return IceDrive.DataTransferPrx.uncheckedCast(prx) # Devuelve el objeto DataTransfer
                    else:
                        raise IceDrive.UnknownBlob(blob_path.name) # Si no está almacenado, se lanza una excepción
                else:
                    raise IceDrive.UnknownBlob(blob_id) # Si no está almacenado, se lanza una excepción
            except IceDrive.TemporaryUnavailable:
                raise IceDrive.TemporaryUnavailable()
        else:
            print("User is not verified.")

