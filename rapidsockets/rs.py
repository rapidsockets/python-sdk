import websocket
import hashlib
import json
import requests
import threading
import collections
import time

class RapidSockets(object):
    def __init__(self, options={}):
        self.gateway = options['gateway'] if 'gateway' in options else 'wss://gateway.rapidsockets.com';
        self.api = options['api'] if 'api' in options else 'https://api.rapidsockets.com'
        self.connection = None;
        self.authenticated = False;
        self.session = hashlib.sha256(b'asd').hexdigest();
        self.packet_queue = [];
        self.cbs = [];
        self.subscriptions = [];

        self.key = options['key'] if 'key' in options else None;

        t = threading.Thread(target=self.start)
        t.start()

    def start(self):
        self.open_connection()

    def open_connection(self):
        self.connection = websocket.WebSocketApp(self.gateway,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)

        self.connection.on_open = self.on_open

        while True:
            self.connection.run_forever()

    def on_open(self, ws):
        packet = {
            'action': 'authorize',
            'payload': {
                'key': self.key
            }
        }

        self.connection.send(json.dumps(packet))

    def on_message(self, ws, packet):
        try:
            packet = json.loads(packet)

            # handle auth fail
            if packet['code'] == 'auth_fail':
                print('Gateway authentication failed');
                return;

            # handle auth success
            if packet['code'] == 'auth_success':
                self.authenticated = True;
                self.flush_queue();
                self.establish_subscriptions();

            # handle ping
            if packet['code'] == 'latency':
                for cb in self.cbs:
                    if cb['operation'] != 'latency':
                        return;

                    cb['callback'](packet['payload']);

            # detect same client
            if 'session' in packet['payload'] and packet['payload']['session'] == self.session:
                return;

            # handle packet
            if packet['code'] == 'message':
                for subscription in self.subscriptions:
                    if subscription['channel'] != packet['payload']['channel']:
                        return;

                    packet['payload']['message'] = json.loads(packet['payload']['message'])

                    subscription['callback'](packet);
        except:
            print('Invalid packet received from Gateway: {}'.format(packet))

    def on_close(self, ws):
        # handled by run_forever
        pass

    def on_error(self, ws, error):
        # handled by run_forever
        pass

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