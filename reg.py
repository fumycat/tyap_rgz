import re
import logging

logging.basicConfig(level=logging.INFO)

q = '(aa)*(ab)*(bb)'


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

if __name__ == '__main__':
    out = parse(('+', 'a+b(c+d)*+ef'))
    logging.info(str(out))

    # logging.info(str(get_disc('b(c+d)*')))


    # regex_test1 = ['a+b(c+d)*+ef']

    # for case in regex_test1:
    #     logging.info('str "' + case + '" res ' + str(re.split('\+(?![^\(]*\))', case)))