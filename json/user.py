import datetime

class User:

  def __init__(self, id, name, birthdate):
    self.id = id
    self.name = name
    if isinstance(birthdate, str):
      self.birthdate = datetime.datetime.strptime(birthdate, "%d %b %y")
    else:
      self.birthdate = birthdate

  def to_dict(u):
    if isinstance(u, User):
      dict = {
        "id": u.id,
        "name": u.name,
        "birthdate": u.birthdate.strftime("%d %b %y"),
        '__class__': 'User',
        '__module__': 'user'
      }
      return dict
    else:
      type_name = u.__class__.__name__
      raise TypeError("Unexpected type {0}".format(type_name))


  def to_object(d):
    if d['__class__'] == 'User' and d['__module__'] == 'user':
      dob = datetime.datetime.strptime(d['birthdate'], "%d %b %y")
      inst = User(d['id'], d['name'], dob)
    else:
      inst = d
    return inst