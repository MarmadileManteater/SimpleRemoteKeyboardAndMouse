
def date(arg = None):
  if arg == None:
    return Date()
  else:
    return Date(arg)

def get_time(date):
  return date.getTime()

__all__ = ["date", "get_time"]
