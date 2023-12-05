import Ice
import sys

Ice.loadSlice("icedrive_blob/icedrive.ice")
import IceDrive

class ClientApp(Ice.Application):
    """Implementation of the Ice.Application for the client."""

    def run(self, args: list) -> int:
        