## RapidSockets Python SDK

### Introduction
This is the official Software Development Kit for Python to interact with the RapidSockets real-time messaging platform.

### Installation
```
pip install rapidsockets
```

### Usage
```python
rs = RapidSockets({
    key: 'your key'
});

def mychannel(packet):
    print(packet['payload']['message']) # my message

rs.subscribe({
    'channel': 'mychannel',
    'callback': mychannel
})

rs.publish({
    'channel': 'mychannel',
    'message': 'my message'
})
```

### Development specific notes
```
# build test wheel
python3 setup.py bdist_wheel

# install test wheel
python3 -m pip install dist/rapidsockets-0.0.2-py3-none-any.whl

# upload to pypi
python3 -m twine upload dist/rapidsockets-0.0.2-py3-none-any.whl
```
