import Ice
import sys
Ice.loadSlice("icedrive_blob/icedrive.ice")
import IceDrive 

class ClientApp(Ice.Application):
    """Implementation of the Ice.Application for the client."""


    def run(self, args: list) -> int:
        print("Client running...")
        print(args[0])

        base = self.communicator().stringToProxy("BlobService -t -e 1.1:tcp -h 127.0.0.1 -p 2000 -t 60000")
        blob = IceDrive.BlobServicePrx.checkedCast(base)
        blob.link("pruebaLink")
        return 0

def client():
    """Run the client."""
    app = ClientApp()
    return app.main(sys.argv)

if __name__ == "__main__":
    client()