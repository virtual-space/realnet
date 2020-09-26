from pynecone import ProtoShell, ProtoCmd
import logging

import asyncio
from bleak import BleakScanner, BleakClient, BleakError
from bleak.uuids import uuidstr_to_str

GattCharacteristicsPropertiesEnum = {
    None: ("None", "The characteristic doesn’t have any properties that apply"),
    1: ("Broadcast", "The characteristic supports broadcasting"),
    2: ("Read", "The characteristic is readable"),
    4: ("WriteWithoutResponse", "The characteristic supports Write Without Response"),
    8: ("Write", "The characteristic is writable"),
    16: ("Notify", "The characteristic is notifiable"),
    32: ("Indicate", "The characteristic is indicatable"),
    64: ("AuthenticatedSignedWrites", "The characteristic supports signed writes"),
    128: ("ExtendedProperties", "The ExtendedProperties Descriptor is present"),
    256: ("ReliableWrites", "The characteristic supports reliable writes"),
    512: ("WritableAuxiliaries", "The characteristic has writable auxiliaries"),
}


class DeviceCmd(ProtoShell):

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

        def __init__(self):
            super().__init__('explore', 'explore a device')

        def add_arguments(self, parser):
            parser.add_argument('address', help="specifies the address of the device")

        def run(self, args):
            address = args.address
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_explore(address))

        async def run_explore(self, address):
            log = logging.getLogger(__name__)
            async with BleakClient(address) as client:

                import sys

                # loop.set_debug(True)
                log.setLevel(logging.DEBUG)
                h = logging.StreamHandler(sys.stdout)
                h.setLevel(logging.DEBUG)
                log.addHandler(h)
                svcs = await client.get_services()
                for service in svcs:
                    log.info("[Service] {0}: {1}".format(service.uuid, service.description))
                    for char in service.characteristics:
                        if "read" in char.properties:
                            try:
                                value = bytes(await client.read_gatt_char(char.uuid))
                            except Exception as e:
                                value = str(e).encode()
                        else:
                            value = None
                        log.info(char)
                        # log.info(
                        #    "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                        #        char.uuid,
                        #        char.handle,
                        #        ",".join(char.properties),
                        #        char.description,
                        #        value,
                        #    )
                        # )
                        for descriptor in char.descriptors:
                            value = await client.read_gatt_descriptor(descriptor.handle)
                            log.info(
                                "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                                    descriptor.uuid, descriptor.handle, bytes(value)
                                )
                            )

        async def run_explore_old(self, address, loop, debug=False):
            log = logging.getLogger(__name__)
            if debug:
                import sys

                # loop.set_debug(True)
                log.setLevel(logging.DEBUG)
                h = logging.StreamHandler(sys.stdout)
                h.setLevel(logging.DEBUG)
                log.addHandler(h)

            async with BleakClient(address, loop=loop) as client:
                x = await client.is_connected()
                log.info("Connected: {0}".format(x))

                for service_uuid, service in client.services.items():
                    # service is instance of 'Windows.Devices.Bluetooth.GenericAttributeProfile.GattDeviceService'
                    log.info(
                        "[Service] {0}: {1}".format(service_uuid, uuidstr_to_str(service_uuid))
                    )
                    # Ugly way to filter out characteristics for this service... I use this since Bleak has
                    # already fetched all characteristics and stored them in `client.characteristics`,
                    # albeit not grouped by service...
                    # Could e.g. be fetched as `chars = await client._get_chars(service)`
                    this_service_chars = list(
                        filter(
                            lambda ch: str(ch[1].Service.Uuid) == service_uuid,
                            client.characteristics.items(),
                        )
                    )
                    for char_uuid, char in this_service_chars:
                        # char is instance of 'Windows.Devices.Bluetooth.GenericAttributeProfile.GattCharacteristic'
                        capabilities = [
                            GattCharacteristicsPropertiesEnum[v][0]
                            for v in [2 ** n for n in range(10)]
                            if (char.CharacteristicProperties & v)
                        ]
                        if "Read" in capabilities:
                            try:
                                char_value = await client.read_gatt_char(char.Uuid.ToString())
                            except BleakError as e:
                                char_value = "ERROR: {0}".format(e)
                        else:
                            char_value = None

                        char_name = (
                            char.UserDescription if char.UserDescription else "None"
                        )
                        log.info(
                            "\t[Characteristic] {0}: ({1}) | Name: {2}, Value: {3} ".format(
                                char_uuid, ",".join(capabilities), char_name, char_value
                            )
                        )
                        # Descriptor handling for Windows will be added in Bleak 0.4.0...
                        # this_char_descriptors = await client._get_descriptors(char)
                        # for descriptor in this_char_descriptors:
                        #     value = await client.read_gatt_descriptor(descriptor.Uuid.ToString())
                        #     log.info(
                        #         "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                        #             descriptor.Uuid.ToString(), descriptor.AttributeHandle, value
                        #         )
                        #     )

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list', 'list devices')

        def run(self, args):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.run_discover())

        async def run_discover(self):
            # devices = await discover()
            devices = await BleakScanner.discover()
            for d in devices:
                print(d)



    def __init__(self):
        super().__init__(   "device",
                            [DeviceCmd.Get(), DeviceCmd.Put(), DeviceCmd.List(), DeviceCmd.Explore(), DeviceCmd.Delete()],
                            "realnet devices")

