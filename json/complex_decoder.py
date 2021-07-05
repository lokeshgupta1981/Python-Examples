import json

class ComplexDecoder(json.JSONDecoder):

  def __init__(self):
    json.JSONDecoder.__init__(
      self,
      object_hook=self.dict_to_object,
    )

  def dict_to_object(self, d):
    if '__class__' in d:
      class_name = d.pop('__class__')
      module_name = d.pop('__module__')
      module = __import__(module_name)
      class_ = getattr(module, class_name)
      args = {
        key: value
        for key, value in d.items()
      }
      inst = class_(**args)
    else:
      inst = d
    return inst