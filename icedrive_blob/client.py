import Ice
import sys
import os
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
        data = self.file.read(size) # Lee size bytes del archivo
        return data

    def close(self, current: Ice.Current = None) -> None:
        """Close the currently opened file."""
        if not self.file.closed: # Si no está cerrado
            self.file.close() # Se cierra el archivo
            current.adapter.remove(current.id) # Se elimina el objeto DataTransfer del adaptador

class ClientApp(Ice.Application):
    """Implementation of the Ice.Application for the client."""
    '''
    def __init__(self):
        directory_name = input("Enter the name of the diretory: ")
        self.b = BlobService(directory_name)
    '''

    def run(self, args: list) -> int:
        print("Client running...")
        print(args[0])

        proxy = self.communicator().stringToProxy("BlobService -t -e 1.1:tcp -h 127.0.0.1 -p 2000 -t 60000") # Convierte la cadena en un proxy
        objeto = IceDrive.BlobServicePrx.uncheckedCast(proxy) # Convierte el proxy a un objeto de tipo BlobServicePrx
        if not objeto:
            print(f"Proxy no válido: {proxy}") # Si el proxy no es válido
            return 2 # Error de conexión
        else:
            directory_name = input("Enter the name of the diretory: ")
            blob = BlobService(directory_name)
            while True:
                print("1. Upload")
                print("2. Download")
                print("3. Link")
                print("4. Unlink")
                print("5. Exit")

                choice = input("Choose an option: ")

                if choice == "1":
                    file_name = input("Enter the name of the file to upload: ")
                    blob_path = Path(blob.directory_path).joinpath(file_name) # Calcula la ruta del archivo
                    data_transfer = DataTransferClient(blob_path)
                    blob_id = blob.upload(data_transfer)
                    print("File uploaded successfully.")
                    print(f"Blob ID: {blob_id}")
                elif choice == "2":
                    blob_id = input("Enter the ID of the blob to download: ")
                    data_transfer = blob.download(blob_id)
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
    return app.main(sys.argv)

if __name__ == "__main__":
    client()