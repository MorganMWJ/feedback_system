import random
import string

def getCode():
    code = ""
    for i in range(6):
        code += random.choice(string.ascii_uppercase + string.digits)
    return code

print(getCode())
