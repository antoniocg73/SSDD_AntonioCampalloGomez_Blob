import Ice
import sys
import os
import hashlib
from icedrive_blob.blob import BlobService
from pathlib import Path
Ice.loadSlice("icedrive_blob/icedrive.ice")
import IceDrive 

class DataTransferClient(IceDrive.DataTransfer):
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
        except Exception as e: # Si se produce un error
            raise IceDrive.FailedToReadData() # Si no se pueden leer los datos, se lanza una excepción   

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        if not self.file.closed: # Si no está cerrado
            self.file.close() # Se cierra el archivo
            current.adapter.remove(current.id) # Se elimina el objeto DataTransfer del adaptador

class ClientApp(Ice.Application):
    """Implementation of the Ice.Application for the client."""
    
    def calculate_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def run(self, args: list) -> int:
        print("Client running...")
        print(args[0])

        proxy = self.communicator().stringToProxy("BlobService -t -e 1.1:tcp -h 127.0.0.1 -p 2000 -t 60000") # Convierte la cadena en un proxy
        blob = IceDrive.BlobServicePrx.uncheckedCast(proxy) # Convierte el proxy a un objeto de tipo BlobServicePrx
        if not blob:
            print(f"Proxy no válido: {proxy}") # Si el proxy no es válido
            return 2 # Error de conexión
        #directory_name = input("Enter the name of the diretory: ")
        # blob = BlobService(directory_name)
        while True:
            print("1. Upload")
            print("2. Download")
            print("3. Link")
            print("4. Unlink")
            print("5. Exit")

            choice = input("Choose an option: ")

            if choice == "1":
                file_name = input("Enter the name of the file to upload: ")
                directory_name = input("Enter the name of the directory: ")
                blob_path = Path(directory_name).joinpath(file_name) # Calcula la ruta del archivo

                hash_object = hashlib.sha256() # Crea un objeto hash
                with open(blob_path, "rb") as original: # Abre el archivo en modo lectura binaria
                    data = original.read()
                    if not data:
                        original.close()
                        break
                    hash_object.update(data) # Actualiza el hash con los datos leídos
                blob_id_original = hash_object.hexdigest() # Devuelve el hash en formato hexadecimal

                data_transfer = DataTransferClient(blob_path)
                #adapter = self.communicator().createObjectAdapter("BlobAdapter") # Crea un adaptador de objetos
                adapter = self.communicator().createObjectAdapterWithEndpoints("BlobAdapter", "default -p 10000") # Crea un adaptador de objetos
                adapter.activate() # Activa el adaptador
                servant_proxy = adapter.addWithUUID(data_transfer) # Añade el objeto al adaptador
                data_transfer_prx = IceDrive.DataTransferPrx.checkedCast(servant_proxy) # Convierte el proxy a un objeto de tipo DataTransferPrx
                blob_id = blob.upload(data_transfer_prx) # Llama a la función upload
                adapter.destroy() # Destruye el adaptador
            
                if blob_id == blob_id_original:
                    print("File uploaded successfully or is already uploaded.")
                    print(f"Blob ID: {blob_id}")
                else:
                    print("File uploaded successfully but the blob ID is different.")
                    print(f"Blob ID: {blob_id}")
                    print(f"Original blob ID: {blob_id_original}")

            elif choice == "2":
                blob_id = input("Enter the ID of the blob to download: ")
                data_transfer_download = blob.download(blob_id) # Llama a la función download
                blob_downloaded = hashlib.sha256() # Crea un objeto hash
                while True:
                    data = data_transfer_download.read(4096) # Lee size bytes del archivo
                    if not data:
                        data_transfer_download.close() # Se cierra el archivo
                        break
                    blob_downloaded.update(data) # Actualiza el hash con los datos leídos
                blob_downloaded = blob_downloaded.hexdigest() # Devuelve el hash en formato hexadecimal
                if blob_id == blob_downloaded: # Si el blob está almacenado
                    print("Blob downloaded successfully.") 
                    print(f"Blob ID download: {blob_downloaded}")
                else:
                    print("Blob downloaded successfully but the blob ID is different.") 
                    print(f"Blob ID download: {blob_downloaded}") 
                    print(f"Original blob ID: {blob_id}") 

            elif choice == "3":
                # Call link function
                blob_id = input("Enter the ID of the blob to link: ")
                blob.link(blob_id)
                print("Blob linked successfully.")

            elif choice == "4":
                blob_id = input("Enter the ID of the blob to unlink: ")
                blob.unlink(blob_id)
                print("Blob unlinked successfully.")

            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("Invalid option. Please try again.")

        return 0

def client():
    """Run the client."""
    app = ClientApp()
    return app.main(sys.argv, "config/blob.config")

if __name__ == "__main__":
    client()