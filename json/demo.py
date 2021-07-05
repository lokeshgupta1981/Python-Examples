import json
from complex_decoder import ComplexDecoder
from user import User
 
# Python dict
user_json = """{
    "name": "Lokesh",
    "id": 39,
    "birthdate": "06 Jan 91",
    "__class__": "User",
    "__module__": "user"
}"""

# Use object_hook to execute custom deserialzation code

user_object = json.loads(user_json, object_hook=User.to_object)

print(user_object)
print(json.dumps(user_object, default=User.to_dict))

# Use ComplexDecoder to execute custom deserialzation code

user_object = json.loads(user_json, cls=ComplexDecoder)

print(user_object)
print(json.dumps(user_object, default=User.to_dict))

