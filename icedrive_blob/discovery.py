"""Servant implementations for service discovery."""

import Ice
Ice.loadSlice('icedrive_authentication/icedrive.ice')
import IceDrive



class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""
    
    def __init__(self):
        self.authentication = set()
        self.directory = set()
        self.blob = set()

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