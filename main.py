#!/usr/bin/env python3
import asyncio
import websockets
import json
import serial
from concurrent.futures import ThreadPoolExecutor

class Server:

    def __init__(self, device, baudrate, loop):
        self._connection = serial.Serial(device, baudrate)
        self._loop = loop
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()
        self._event.set()
        self._data = {
            'insolation': 0,
            'temperature': 0,
        }

    @staticmethod
    def get_serial_data(connection):
        return connection.readline()

    def __call__(self, websocket, path):
        while True:

            if not websocket.open:
                break

            if not self._lock.locked() and self._connection.inWaiting() >= 5:
                with (yield from self._lock):
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        serial_data = yield from self._loop.run_in_executor(executor, self.get_serial_data, self._connection)
                    if len(serial_data) >= 5:
                        serial_data = serial_data.rstrip().decode('utf-8').split(';')
                        print("Recived {}".format(serial_data))
                        self._event.clear()
                        self._data = {
                            'insolation': serial_data[0],
                            'temperature': serial_data[1],
                        }
                        self._event.set()

            self._event.wait()  # Wait until the new data is ready
            yield from websocket.send(json.dumps(self._data))
            print("Sent {}".format(self._data))
            diode = yield from websocket.recv()

            yield from asyncio.sleep(2)


if __name__ == '__main__':
    server = asyncio.coroutine(Server('/dev/ttyACM0', 9600, asyncio.get_event_loop()))

    start_server = websockets.serve(server, 'localhost', 8889)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
