"""Servant implementations for service discovery."""

import Ice
import IceDrive
import random



class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    
    def __init__(self):
        self.authentication = set() # Conjunto de servicios de autenticación
        self.directory = set() # Conjunto de servicios de directorio
        self.blob = set() # Conjunto de servicios de blob

    def announceAuthentication(self, proxy: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        self.authentication.add(proxy)
        print(proxy)
        
    def announceDirectoryService(self, proxy: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        self.directory.add(proxy)
        print(proxy)

    def announceBlobService(self, proxy: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        self.blob.add(proxy)
        print(proxy)

    def getAuthentication(self) -> IceDrive.AuthenticationPrx:
        """Obtener un servicio de autenticación aleatorio."""
        if not self.authentication:
            return None  # No hay servicios de autenticación disponibles
        return random.choice(list(self.authentication))

    def getDirectoryService(self) -> IceDrive.DirectoryServicePrx:
        """Obtener un servicio de directorio aleatorio."""
        if not self.directory:
            return None  # No hay servicios de directorio disponibles
        return random.choice(list(self.directory))

    def getBlobService(self) -> IceDrive.BlobServicePrx:
        """Obtener un servicio de blob aleatorio."""
        if not self.blob:
            return None  # No hay servicios de blob disponibles
        return random.choice(list(self.blob))