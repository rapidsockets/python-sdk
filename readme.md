## RapidSockets Python SDK

### Introduction
This is the official Software Development Kit for Python to interact with the RapidSockets real-time messaging platform.

### Installation
```
pip install rapidsockets
```

### Quickstart
```python
from rapidsockets import RapidSockets
import time

# initialize and open a connection to the RapidSockets Gateway
rs = RapidSockets({
    'key': 'your multi key'
})

# the callback function run on a new message to channel "mytest"
def mytest(packet):
    print(packet)

# start listening for new messages on channel "mytest"
rs.subscribe({
    'channel': 'mytest',
    'callback': mytest
})

# as a test, publish messages to channel "mytest" every two seconds
while True:
    rs.publish({
        'channel': 'mytest',
        'message': 'test message'
    })
    time.sleep(2)
```

### Development specific notes
```
# build test wheel
python3 setup.py bdist_wheel

# install test wheel
python3 -m pip install dist/rapidsockets-0.0.5-py3-none-any.whl

# upload to pypi
python3 -m twine upload dist/rapidsockets-0.0.5-py3-none-any.whl
```
