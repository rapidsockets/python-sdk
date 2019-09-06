from setuptools import setup

def readme():
    with open('readme.md') as f:
        return f.read()[0:]

setup(name='rapidsockets',
      version='0.0.4',
      description='Official Python SDK for the RapidSockets platform',
      long_description=readme(),
      long_description_content_type='text/markdown',
      keywords='websockets',
      url='https://github.com/rapidsockets/python',
      author='RapidSockets',
      author_email='support@rapidsockets.com',
      license='MIT',
      packages=['rapidsockets'],
      install_requires=['websocket_client', 'requests'],
      zip_safe=False)
