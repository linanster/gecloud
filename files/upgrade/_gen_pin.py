import uuid, sys

pin = uuid.uuid4().hex

print('{}-{}'.format(sys.argv[1], pin))
