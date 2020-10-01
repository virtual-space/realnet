from pynecone import ProtoShell, ProtoCmd


import bluetooth
import asyncio


class Device(ProtoShell):

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete', 'delete a device')

    class Put(ProtoCmd):

        def __init__(self):
            super().__init__('put', 'put a device')

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get', 'get a device')

    class Explore(ProtoCmd):

        class Discoverer(bluetooth.DeviceDiscoverer):
            def pre_inquiry(self):
                self.done = False

            def device_discovered(self, address, device_class, name):
                print("%s - %s - %s" % (address, name, device_class))

            def inquiry_complete(self):
                self.done = True


        def __init__(self):
            super().__init__('explore', 'explore a device')

        def add_arguments(self, parser):
            parser.add_argument('address', help="specifies the address of the device")

        def run(self, args):
            address = args.address
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_explore(address))

        async def run_explore(self, address):

            services = bluetooth.find_service(address=address)

            for service in services:
                print(service)

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list devices')

        def run(self, args):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_discover())

        async def run_discover(self):
            nearby_devices = bluetooth.discover_devices(lookup_class=True,lookup_names=True)

            for bdaddr in nearby_devices:
                print(bdaddr)


    def __init__(self):
        super().__init__(   "device",
                            [Device.Get(),
                             Device.Put(),
                             Device.List(),
                             Device.Explore(),
                             Device.Delete()],
                            "realnet devices")

