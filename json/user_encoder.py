import json
import datetime
from user import User

class UserEncoder(json.JSONEncoder):

	def default(self, u):

		if isinstance(u, User):
			dict = {
				"id": u.id,
				"name": u.name,
				"birthdate": u.birthdate.strftime("%d %b %y")
			}
			return dict
		else:
			type_name = u.__class__.__name__
			raise TypeError("Unexpected type {0}".format(type_name))