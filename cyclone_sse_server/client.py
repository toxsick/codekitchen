from sseclient import SSEClient

messages = SSEClient('http://localhost:8888?channels=base')
for msg in messages:
    print msg.__dict__
