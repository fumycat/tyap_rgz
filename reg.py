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

logging.basicConfig(level=logging.INFO, format='%(message)s')

def get_conc(string):
    logging.info('get_conc call ' + str(string))
    result = []
    
    p = 0
    stack = ''
    for i, c in enumerate(string):
        if p > 0:
            if c == ')':
                p -= 1
                if p > 0:
                    stack += c
                else:
                    stack += c
            elif c == '(':
                p += 1
                stack += c
            else:
                stack += c
        else:
            if c == '(':
                p += 1
                stack += c
            elif c == ')':
                logging.error('invalid ) in get_conc')
            elif c == '+':
                result.append(stack)
                stack = ''
            else:
                stack += c

    result.append(stack)

    logging.info('get_conc return ' + str(result))

    return result


def get_disc(string):
    logging.info('get_disc call ' + str(string))
    result = []

    p = 0
    stack = ''
    for i, c in enumerate(string):
        if p > 0:
            if c == ')':
                p -= 1
                stack += c
                
                if p == 0:
                    if i + 1 < len(string) and string[i+1] == '*':
                        result.append([True, stack])
                    else:
                        result.append([False, stack])
                    stack = ''
                else:
                    ...
            elif c == '(':
                p += 1
                stack += c
            else:
                stack += c
        else:
            if c == '(':
                p += 1
                stack += c
            elif c == ')':
                logging.error('invalid ) in get_disc')
            elif c == '*':
                pass
            else:
                result.append([False, c])

    logging.info('get_disc return ' + str(result))

    return result

def check(expression):  
    open_tup = tuple('(') 
    close_tup = tuple(')') 
    map = dict(zip(open_tup, close_tup)) 
    queue = [] 
  
    for i in expression: 
        if i in open_tup: 
            queue.append(map[i]) 
        elif i in close_tup: 
            if not queue or i != queue.pop(): 
                return False
    if not queue: 
        return True
    else: 
        return False

def unp(string):
    #if string.startswith('(') and string.endswith(')') and string.count('(') == 1 and string.count(')') == 1:
    #    return string[1:-1]
    if string.startswith('(') and string.endswith(')'):
        if check(string[1:-1]):
            return string[1:-1]
    return string

class sNode(object):
    def __init__(self, string):
        # logging.info('sNode ' + string)
        self.string = string
        self.string = unp(self.string)
        self.childs = []
        self.parse()

    def __str__(self):
        return f'[*][{self.string}] <' + ', '.join(str(x) for x in self.childs) + '>'

    def parse(self):
        if any(x in self.string for x in ['+', '*', '(', ')']):
            self.childs = [pNode(self.string)]
        else:
            self.childs = [self.string]
        

class xNode(object):
    def __init__(self, string):
        # logging.info('xNode ' + string)
        self.string = string
        self.string = unp(self.string)
        self.childs = []
        self.parse()

    def __str__(self):
        return f'[x][{self.string}] <' + ', '.join(str(x) for x in self.childs) + '>'

    # def parse(self):
    #     if any(x in self.string for x in ['+', '*', '(', ')']):
    #         self.childs = [pNode(x) for x in get_disc(self.string)]

    def parse(self):
        if any(x in self.string for x in ['+', '*', '(', ')']):
            for is_star, node in get_disc(self.string):
                if is_star:
                    self.childs.append(sNode(node))
                else:
                    self.childs.append(pNode(node))
        else:
            self.childs = [self.string]
        

class pNode(object):
    def __init__(self, string):
        # logging.info('pNode ' + string)
        self.string = string
        self.string = unp(self.string)
        self.childs = []
        self.parse()

    def __str__(self):
        return f'[+][{self.string}] <' + ', '.join(str(x) for x in self.childs) + '>'

    def parse(self):
        if any(x in self.string for x in ['+', '*', '(', ')']):
            self.childs = [xNode(x) for x in get_conc(self.string)]
        else:
            self.childs = [self.string]


def normal_output(node_obj, deep=0):

    def normal_t(x_obj):
        if type(x_obj) is xNode:
            return 'x'
        elif type(x_obj) is pNode:
            return '+'
        elif type(x_obj) is sNode:
            return '*'

    for child in node_obj.childs:
        if type(child) is str:
            print('  ' * deep + normal_t(node_obj) + ' ' + child)
        else:
            normal_output(child, deep + 1)


def class_gen(tree_obj):
    logging.info('call class_gen ' + str(tree_obj))
    if type(tree_obj) is sNode:
        # ['c', 'd'] -> ['c', 'd', 'cd', 'dc', 'cc', 'dd', ...]
        # ['ab'] -> ['ab', 'abab', ...]
        z = []
        for child in tree_obj.childs:
            z += class_gen(child)
        if len(z) == 1:
            return list(itertools.repeat(z[0], 3))
        else:
            return ['', 'y', 'yy']
    elif type(tree_obj) is pNode:
        # ['a'], ['b', 'bc' ,'bd', ...], ['ef'] -> ['a', 'b', 'bc' ,'bd', ..., 'ef']
        z = []
        for child in tree_obj.childs:
            z += class_gen(child)
        logging.info('class_gen(pNode) return ' + str(z))
        return z
    elif type(tree_obj) is xNode:
        # ['b'], ['', 'c', 'd', 'cc', 'cd', ...] -> ['b', 'bc' ,'bd', ...]
        z = []
        for child in tree_obj.childs:
            z += class_gen(child)
        y = []
        logging.info('z ' + str(z)) # <----
        for t in itertools.product(*z):
            y.append(''.join(t))
        logging.info('class_gen(xNode) return ' + str(y))
        return y

    elif type(tree_obj) is str:
        # 'a' -> ['a']
        return [tree_obj]


def parse(string):
    '''
    deprecated
    '''
    logging.info('TRACE ' + str(string))
    if len(string[1]) == 1:
        if string[1] in ['*', '+']:
            logging.error('parse invalid symbol')
        logging.info('END ' + str(string))
        return string[1]

    tree = []
    if string[0] == '+':
        tree = [('x', parse(('x', x))) for s, x in get_conc(string)]
    elif string[0] == 'x':
        tree = [(s, parse((s, x))) for s, x in get_disc(string)]
    elif string[0] == '*':
        tree = ('+', parse(('+', string[1])))


    logging.info('END ' + str(tree))
    return tree


@print_calls
def build(regular, dim):
    if type(regular[1]) in (list, tuple) or (type(regular[1]) is str and regular[0] == '*'):
        if regular[0] == '+':
            tt = [build(x, dim) for x in regular[1]]
            if type(tt) is list and len(tt) == 1 and type(tt[0]) is list:
                return tt[0]
            else:
                return tt 
        elif regular[0] == 'x':
            return [''.join(y) for y in itertools.product(*[build(x, dim) for x in regular[1]])]
        elif regular[0] == '*':
            if type(regular[1]) is not str:
                bts = build(regular[1], dim)
            else:
                bts = [regular[1]]
            logging.info('bts ' + repr(bts))

            xts = []
            for e in bts:
                if type(e) is list and len(e) == 1:
                    xts.append(e[0])
                elif type(e) is str:
                    xts.append(e)
            if xts:
                bts = xts
            bts = bts_ret(bts)
            # print("^-^ HERE", regular, bts)
            # always list tho?

            logging.info('bts ' + repr(bts))

            btl = [x for x in bts]
            #if type(btl[0]) is list:
            #    btl = btl[0] 
            i2 = 1
            while len(btl[-1]) < dim[1]:
                t = []
                for i in range(len(bts) * i2):
                    for e in bts:
                        t.append(btl[-(i+1)] + e)
                btl += t
                i2 **= 2
                logging.info(str(i2) + ' ' +str(btl))
            return [''] + btl
        else:
            logging.error('build invalid regular[0]')
    else:
        return regular[1]


def generate(built, minlen, maxlen):
    logging.info('GEN ' + repr(built))
    from pprint import pprint
    pprint(built)
    built = build(('+', built), (None, maxlen))
    logging.info('generate built ' + repr(built))
    if all(type(i) is str for i in built):
        logging.info('1')
        built.sort()
        return list(set([x for x in built if len(x) >= minlen and len(x) <= maxlen]))
    else:
        logging.info('2')
        # return list(set(flatten([x for x in built if len(x) >= minlen and len(x) <= maxlen])))
        logging.info(repr([''.join(z) for z in itertools.product(*built)]))
        logging.info('here' + repr( [x for x in itertools.product(built[0], built[1])]))
        # logging.info(repr())
        # return [x+y for x,y in itertools.product(built[0], built[1])] + list(set([x for x in sorted([''.join(z) for z in itertools.product(*built)] + list(flatten(built))) if len(x) >= minlen and len(x) <= maxlen]))


if __name__ == '__main__':

    i_1 = pNode('a+b(c+d)*+ef')
    logging.info(i_1)
    normal_output(i_1)

    logging.info(str(class_gen(i_1)))

    #i_2 = pNode('((a+b+c)(a+b+c))*cc')
    #logging.info(i_2)
    #normal_output(i_2)


