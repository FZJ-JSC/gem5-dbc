import re
import sys

def fatal_error(message: str):
    print(message)
    sys.exit(1)
    

def multiply_int_units(value, factor):
    # type: (str,int) -> str
    p = re.compile(r'([+-]?[0-9]+([.][0-9]*)?|[.][0-9]+)(\w+)')
    n, _n, u = p.match(value).groups()
    m = factor * int(n)
    return "{}{}".format(m,u)

def multiply_float_units(value, factor):
    # type: (str,float) -> str
    p = re.compile(r'([+-]?[0-9]+([.][0-9]*)?|[.][0-9]+)(\w+)')
    n, _n, u = p.match(value).groups()
    m = factor * float(n)
    return "{}{}".format(m,u)

def divide_float_units(value, factor):
    # type: (str,float) -> str
    p = re.compile(r'([+-]?[0-9]+([.][0-9]*)?|[.][0-9]+)(\w+)')
    n, _n, u = p.match(value).groups()
    m = float(n) / factor
    return "{}{}".format(m,u)

def divide_int_units(value, factor):
    # type: (str,int) -> str
    p = re.compile(r'([+-]?[0-9]+([.][0-9]*)?|[.][0-9]+)(\w+)')
    n, _n, u = p.match(value).groups()
    m = int(n) / factor
    return "{}{}".format(int(m),u)

def divide_float_unitless(value1, value2):
    # type: (str,str) -> int
    p = re.compile(r'([+-]?[0-9]+([.][0-9]*)?|[.][0-9]+)(\w+)')
    n1, _n1, u1 = p.match(value1).groups()
    n2, _n2, u2 = p.match(value2).groups()
    m = float(n1) / float(n2)
    return m

def replace_unicode_with_str(d):
    n = {}
    for k, v in d.items():
        if isinstance(v, dict):
            n[k]=replace_unicode_with_str(v)
        else:
            n[k] = str(v) if isinstance(v, str) else v
    return n
