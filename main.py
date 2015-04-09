#!/usr/bin/env python3
import asyncio
import websockets
import json
import serial
from concurrent.futures import ThreadPoolExecutor


class Server:

    def __init__(self, serial_reader):
        self._serial_reader = serial_reader

    def __call__(self, websocket, path):
        data = None
        while True:

            if not websocket.open:
                break

            newdata = yield from self._serial_reader.data
            if newdata != data:
                data = newdata
                yield from websocket.send(json.dumps(data))
                print("Sent {}".format(data))

            yield from asyncio.sleep(0.5)


class SerialReader:

    def __init__(self, device, baudrate, loop):
        self._connection = serial.Serial(device, baudrate)
        self._loop = loop

        self._event = asyncio.Event()
        self._event.set()
        self._data = {
            'insolation': 0,
            'temperature': 0,
        }

    @property
    def data(self):
        yield from self._event.wait()
        return self._data

    @staticmethod
    def _get_serial_data(connection):
        return connection.readline()

    def __call__(self):
        while True:
            if self._connection.inWaiting() >= 5:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    serial_data = yield from self._loop.run_in_executor(
                        executor, self._get_serial_data, self._connection)
                    if len(serial_data) >= 5:
                        serial_data = serial_data.rstrip().decode('utf-8').split(';')
                        print("Read {}".format(serial_data))
                        self._event.clear()
                        self._data = {
                            'insolation': serial_data[0],
                            'temperature': serial_data[1],
                        }
                        self._event.set()
            yield from asyncio.sleep(1)


if __name__ == '__main__':
    serial_reader = SerialReader('/dev/ttyACM0', 9600, asyncio.get_event_loop())
    server = asyncio.coroutine(Server(serial_reader))
    serial_reader = asyncio.coroutine(serial_reader)
    start_server = websockets.serve(server, 'localhost', 8889)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_until_complete(serial_reader())
    asyncio.get_event_loop().run_forever()
