import asyncio
import json


@asyncio.coroutine
def listen_client(loop):
    """ Create client to listen for lines of data"""
    reader, writer = yield from asyncio.open_unix_connection(
        path='/tmp/mys.sock', loop=loop)
    # uncomment following lines and remove
    # open_unix_connection line to use port
    # reader, writer = yield from asyncio.open_connection(host='127.0.0.1',
    #                                                     port=8877,
    #                                                     loop=loop)

    while True:
        data = yield from reader.readline()

        if data:
            cleaned = json.loads(data.decode())
            print('Received: %s' % cleaned)
            # DO SOMETHING :)
        else:
            print('Close the socket')
            writer.close()
            return


loop = asyncio.get_event_loop()
# Listen to messages until Ctrl+C is pressed
coro = loop.run_until_complete(listen_client(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

loop.close()
