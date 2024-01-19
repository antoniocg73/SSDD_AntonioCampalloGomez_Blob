"""Authentication service application."""
import sys
from typing import List
import Ice
from .blob import BlobService
from .discovery import Discovery
import IceDrive
import IceStorm
import threading
import time

class BlobApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""
    def announce(discovery_proxy, blob):
        while True:
            discovery_proxy.announceBlobService(blob)
            time.sleep(5) 
    
    def run(self, args: List[str]) -> int:
        """Execute the code for the BlobApp class."""        
        properties = self.communicator().getProperties() # Obtiene las propiedades del comunicador
        topic_name = properties.getProperty("Discovery.Topic") # Obtiene el nombre del topic
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(self.communicator().propertyToProxy("IceStorm.TopicManager.Proxy")) # Obtiene el proxy del topic manager
        try:
            topic = topic_manager.retrieve(topic_name) # Obtiene el topic
        except IceStorm.NoSuchTopic:
            topic = topic_manager.create(topic_name) # Si no existe, se crea el topic
        
        adapter = self.communicator().createObjectAdapter("BlobAdapter") # Se crea un adaptador
        adapter.activate() # Se activa el adaptador
        
        discovery_servant = Discovery() # Se crea el servant
        discovery_proxy = adapter.addWithUUID(discovery_servant) # Se añade el servant al adaptador
        #discovery_topic = topic.subscribeAndGetPublisher({}, discovery_proxy) # Se suscribe el servant al topic
        discoveryProxy = IceDrive.DiscoveryPrx.uncheckedCast(topic.getPublisher()) # Se obtiene el proxy del servant
        
        directory = self.communicator().getProperties().getProperty("directoryName") # Obtiene el nombre del directorio
        blob_servant = BlobService(directory, discovery_servant) # Se crea el servant
        blob_proxy = adapter.addWithUUID(blob_servant) # Se añade el servant al adaptador
        blob_proxy_cast = IceDrive.BlobServicePrx.uncheckedCast(blob_proxy) # Se obtiene el proxy del servant
        
        #ANNOUNCE
        threading.Thread(target=BlobApp.announce, args=(discoveryProxy, blob_proxy_cast), daemon=True).start() # Se lanza un hilo para anunciar el servant
        
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0

def main():
    """Handle the icedrive-authentication program."""
    app = BlobApp()
    return app.main(sys.argv, "config/blob.config")

