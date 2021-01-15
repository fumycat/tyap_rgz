import re
import logging
import itertools

import functools

def print_calls(func):
    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        # print('function call ' + func.__name__ + '()')
        argnames = func.__code__.co_varnames[:func.__code__.co_argcount] 
        print('< ' + ', '.join( '% s = % r' % entry for entry in zip(argnames, func_args[:len(argnames)])))
        retval = func(*func_args,**func_kwargs)
        print('> ' + repr(retval))
        return retval
    return wrapper

logging.basicConfig(level=logging.INFO)

def get_disc(string):
    logging.info('get_disc call ' + str(string))
    result = []

    p = 0
    stack = ''
    for i, c in enumerate(string[1]):
        if p > 0:
            if c == ')':
                p -= 1
                if p == 0:
                    if i + 1 < len(string[1]) and string[1][i+1] == '*':
                        result.append(('*', stack))
                    else:
                        result.append(('+', stack))
                    stack = ''
            elif c == '(':
                p += 1
            else:
                stack += c
        else:
            if c == '(':
                p += 1
            elif c == ')':
                logging.error('get_disc invalid )')
            elif c == '*':
                pass
            else:
                result.append(('+', c))

    logging.info('get_disc return ' + str(result))
    return result


def parse(string):
    logging.info('TRACE ' + str(string))
    if len(string[1]) == 1:
        if string[1] in ['*', '+']:
            logging.error('parse invalid symbol')
        logging.info('END ' + str(string))
        return string[1]

    tree = []
    if string[0] == '+':
        tree = [('x', parse(('x', x))) for x in re.split('\+(?![^\(]*\))', string[1])]
    elif string[0] == 'x':
        tree = [(s, parse((s, x))) for s, x in get_disc(string)]
    elif string[0] == '*':
        tree = ('+', parse(('+', string[1])))


    logging.info('END ' + str(tree))
    return tree


# @print_calls
def build(regular, dim):
    if type(regular[1]) in (list, tuple):
        if regular[0] == '+':
            return [build(x, dim) for x in regular[1]]
        elif regular[0] == 'x':
            return [''.join(y) for y in itertools.product(*[build(x, dim) for x in regular[1]])]
        elif regular[0] == '*':
            bts = build(regular[1], dim)

            # always list tho?
            btl = [x for x in bts]
            i2 = 1
            while len(btl[-1]) < dim[1]:
                t = []
                for i in range(len(bts) * i2):
                    for e in bts:
                        t.append(btl[-(i+1)] + e)
                btl += t
                i2 *= 2
            return [''] + btl
        else:
            logging.error('build invalid regular[0]')
    else:
        return regular[1]

def generate(built, minlen, maxlen):
    built = build(('+', out), (None, maxlen))
    return [x for x in [''.join(z) for z in itertools.product(*built)] if len(x) >= minlen and len(x) <= maxlen]

if __name__ == '__main__':
    out = parse(('+', 'a+b(c+d)*+ef'))
    logging.info(str(out))
    
    from pprint import pprint
    pprint(out)
    
    print(generate(out, 0, 7))

    # logging.info(str(get_disc('b(c+d)*')))


    # regex_test1 = ['a+b(c+d)*+ef']

    # for case in regex_test1:
    #     logging.info('str "' + case + '" res ' + str(re.split('\+(?![^\(]*\))', case)))