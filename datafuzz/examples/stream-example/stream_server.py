import asyncio
import json
import os

from datetime import datetime
from datafuzz.generators import DatasetGenerator


def get_dataset():
    """ Generate example dataset and yield from output """
    dataset = DatasetGenerator({
        'num_rows': 100,
        'output': 'list',
        'schema': {'name': 'faker.name',
                   'phone_number': 'faker.phone_number',
                   'group_id': range(2, 5),
                   'called_by': ['robo', 'associate', 'manager']},
        'start_time': datetime(2017, 1, 1, 23, 22),
        'end_time': datetime(2017, 7, 1, 22, 14),
        'increments': 'hours'})
    dataset.generate()
    yield from dataset.to_output()


@asyncio.coroutine
def send_data(reader, writer):
    """ Send serialized data to socket or port """
    dataset = get_dataset()
    for data in dataset:
        data_str = json.dumps(data) + '\n'
        print("Send: %r" % data)
        writer.write(bytes(data_str, encoding='utf-8'))
        yield from writer.drain()
    writer.close()


loop = asyncio.get_event_loop()
# uncomment following line (and remove start_unix_server line) to use port
# coro = asyncio.start_server(send_data, '127.0.0.1', 8877, loop=loop)
coro = asyncio.start_unix_server(send_data, '/tmp/mys.sock', loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
os.remove('/tmp/mys.sock')
