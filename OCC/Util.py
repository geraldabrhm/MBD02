import re

def parseTxnElmt(elmt: str):
    try:
        if(elmt[0] in ['R', 'W']):
            res = re.search('(^[1-9]\d*)+\(+(\w)+\)', elmt[1:])
            txNum = res.group(1)
            data = res.group(2) # Handle only 1 char
            return elmt[0], int(txNum), data
        elif(elmt[0] == 'C'):
            return elmt[0], int(elmt[1:]), None
        else:
            return "[Corner case] transaction element not known"
    except:
        print("Error occured")
        return False
