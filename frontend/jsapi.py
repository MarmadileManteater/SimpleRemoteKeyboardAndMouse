
def set_timeout(callback, timeout):
  return setTimeout(callback, timeout)

def encode_uri(uri):
  return encodeURI(uri)

def type_of(variable):
  return JS('typeof variable')

__all__ = ['set_timeout', 'encode_uri', 'type_of']
