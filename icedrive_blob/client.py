import Ice
import sys

Ice.loadSlice("icedrive_blob/icedrive.ice")
import IceDrive

class ClientApp(Ice.Application):
    """Implementation of the Ice.Application for the client."""

    def run(self, args: list) -> int:
        print("Client running...")
        print(args[0])

        base = self.communicator().stringToProxy("3e3cd43a-e431-4eba-85fb-f9021ccf6948 -t -e 1.1:tcp -h 1 127.0.0.1 -p 2000 -t 60000")
        blob = IceDrive.BlobServicePrx.checkedCast(base)