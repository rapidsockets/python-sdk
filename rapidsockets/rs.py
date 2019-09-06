import websocket
import hashlib
import json
import requests
import threading
import collections
import time
import random

class RapidSockets(object):
    def __init__(self, options={}):
        rand1 = random.uniform(0, 1)
        rand2 = random.uniform(0, 1)
        rand3 = random.uniform(0, 1)

        self.gateway = options['gateway'] if 'gateway' in options else 'wss://gateway.rapidsockets.com'
        self.api = options['api'] if 'api' in options else 'https://api.rapidsockets.com'
        self.connection = None
        self.authenticated = False
        self.session = hashlib \
            .sha256('{}-{}-{}'.format(rand1, rand2, rand3).encode()) \
            .hexdigest()
        self.packet_queue = []
        self.cbs = []
        self.subscriptions = []

        self.key = options['key'] if 'key' in options else None

        self.start()

    def start(self):
        t = threading.Thread(target=self.open_connection)
        t.start()

    def open_connection(self):
        self.connection = websocket.WebSocketApp(self.gateway,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)

        self.connection.on_open = self.on_open

        self.connection.run_forever()

    def on_open(self):
        print('Connection established with RapidSockets Gateway')

        packet = {
            'action': 'authorize',
            'payload': {
                'key': self.key
            }
        }

        self.connection.send(json.dumps(packet))

    def on_message(self, packet):
        try:
            packet = json.loads(packet)

            # handle auth fail
            if packet['code'] == 'auth_fail':
                print('RapidSockets Gateway authentication failed')
                return

            # handle auth success
            if packet['code'] == 'auth_success':
                self.authenticated = True
                self.flush_queue()
                self.establish_subscriptions()

            # handle ping
            if packet['code'] == 'latency':
                for cb in self.cbs:
                    if cb['operation'] != 'latency':
                        return

                    cb['callback'](packet['payload'])

            # detect same client
            if 'session' in packet['payload'] and packet['payload']['session'] == self.session:
                return

            # handle packet
            if packet['code'] == 'message':
                for subscription in self.subscriptions:
                    if subscription['channel'] != packet['payload']['channel']:
                        return

                    packet['payload']['message'] = json.loads(packet['payload']['message'])

                    subscription['callback'](packet)
        except:
            print('Invalid packet received from RapidSockets Gateway: {}'.format(packet))

    def on_close(self):
        print('Connection to the RapidSockets Gateway was lost')

        self.authenticated = False

        time.sleep(3)

        print('Attempting to reconnect to the RapidSockets Gateway...')

        self.start()

    def on_error(self, error):
        raise error

    def flush_queue(self):
        if len(self.packet_queue) > 0:
            packets = self.packet_queue[:]
            self.packet_queue = []

            for packet in packets:
                self.connection.send(json.dumps(packet))

    def establish_subscriptions(self):
        for subscription in self.subscriptions:
            packet = {
                'action': 'subscribe',
                'payload': {
                    'channel': subscription['channel']
                }
            }

            self.connection.send(json.dumps(packet))

    def on(self, operation, callback):
        if not isinstance(channel, str):
            print('Channel must be a string')
            return
        if not isinstance(callback, collections.Callable):
            print('Callback must be a function')
            return

        self.cbs.append({
            'operation': operation,
            'callback': callback
        })

    def subscribe(self, options):
        if not isinstance(options['channel'], str):
            print('Channel must be a string')
            return
        if not isinstance(options['callback'], collections.Callable):
            print('Callback must be a function')
            return

        self.subscriptions.append({
            'channel': options['channel'],
            'callback': options['callback']
        })

        packet = {
            'action': 'subscribe',
            'payload': {
                'channel': options['channel']
            }
        }

        if not self.authenticated:
            return

        self.connection.send(json.dumps(packet))

    def publish(self, options):
        requests.post(
            self.api + '/v1/messages',
            headers={
                'Authorization': self.key,
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'channel': options['channel'],
                'message': json.dumps(options['message'])
            })
        )
