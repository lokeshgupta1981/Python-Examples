import bcrypt
 
passwd = b'user_password'
 
# Hash a password for the first time
hashed = bcrypt.hashpw(passwd, bcrypt.gensalt(10))
 
# Match with already stored hashed password
matched = bcrypt.checkpw(passwd, hashed)
 
print ("Password match is : " , matched)