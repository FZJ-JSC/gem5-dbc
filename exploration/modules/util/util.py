import re

# power of 2 prefixes
kibi = 1024
mebi = kibi * 1024
gibi = mebi * 1024
tebi = gibi * 1024
pebi = tebi * 1024
exbi = pebi * 1024

binary_prefix = {
    'Ei': exbi,
    'E' : exbi,
    'Pi': pebi,
    'P' : pebi,
    'Ti': tebi,
    'T' : tebi,
    'Gi': gibi,
    'G' : gibi,
    'Mi': mebi,
    'M' : mebi,
    'ki': kibi,
    'k' : kibi,
}

def parse_number(txt: str):
  if(txt is not None):
    num = txt #capture_number(txt)
    try:
        return float(num)
    except ValueError:
      pass
    try:
        return int(num)
    except ValueError:
        pass
    return num
  else:
    return 'None'

def toBinaryInteger(value: str, unit = 'B'):
    rx = re.compile("([0-9]*)({})({})".format( '|'.join([ k for k,v in binary_prefix.items() ]), unit))
    res = 0
    if rx.match(value):
        m = rx.search(value)
        res = parse_number(m.group(1))*binary_prefix[m.group(2)]

    return res
  