###### range is a type in Python

# <class 'range'>
type_info = type(range(10)) 

###### Loop through range

# 0 1 2 3 4 5 6 7 8 9
x = range(10)
for n in x:
  print(n, end=" ")     
       
###### Valid Usages

# 0 1 2 3 4 5 6 7 8 9
range(10)        

# 2 3 4 5 6 7 8 9  
range(2, 10)

# 2 4 6 8
range(2, 10, 2)

# 10 8 6 4
range(10, 2, -2)

####### Invalid Usages

# Floats are not allowed
# range(3.3)

# Characters are not allowed
# range('a', 'd')

####### Access items in range

x = range(10)

# First item in range
print( x[0] )   # 0

# Last item in range
print( x[-1] )  # 9

# 4th item in range
print( x[3] )   # 3

# Check if a number is part of the sequence
print (12 in x)     # False
print (8 in x)      # True

# Supports index()
print( x.index(3) )   # 3

###### Supports slicing

print( x[5] )       # 5
print( x[2:] )      # range(2, 10)
print( x[:5] )      # range(0, 5)
print( x[2:5] )     # range(2, 5)
print( x[-1] )      # 9
