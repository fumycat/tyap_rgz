# λ
from tkinter import Tk, Text, BOTH, W, N, E, S, Scrollbar, Listbox, IntVar, messagebox
from tkinter.ttk import Frame, Button, Label, Style, Separator, Spinbox
# from z import *
from reg import *
import re
import os
import copy
import time
import itertools
import logging
import functools
from collections.abc import Iterable
from collections import OrderedDict

def print_calls(func):
    @functools.wraps(func)
    def wrapper(*func_args, **func_kwargs):
        # print('function call ' + func.__name__ + '()')
        argnames = func.__code__.co_varnames[:func.__code__.co_argcount] 
        logging.info('< ' + ', '.join( '% s = % r' % entry for entry in zip(argnames, func_args[:len(argnames)])))
        retval = func(*func_args,**func_kwargs)
        logging.info('> ' + repr(retval))
        return retval
    return wrapper

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    handlers=[
        logging.FileHandler('logs\\log ' + time.strftime('%d %b %H_%M_%S') + '.txt'),
        logging.StreamHandler()
    ]
)

rmp = lambda x: x.replace('{', '').replace('}', '').replace('(', '').replace(')', '')

#with open('input.txt', encoding='utf-8') as f:
#    fline, *p = [x.strip() for x in f.readlines()]

orig_rules = dict()
rules = dict()
vt = list()
vn = list()
s = str()

# vt, vn, _, s = map(str.strip, map(rmp, re.split(',(?![^{}]*})', fline[1:])))
# vt, vn = [x.strip() for x in vt.split(',')], [x.strip() for x in vn.split(',')]


# pravo = True

# for rule in p:
#     rule = rule.replace(' ', '')
#     f, t = rule.split('->')
#     rules[f] = t.split('|')


# utils

get_t = lambda x: ''.join(i for i in x if i in vt)


def ftest():
    logging.warning('ftest')
    with open('input.txt', encoding='utf-8') as f:
        proc_gram(f.read())
    remove_lambda_rules()
    logging.info('remove_lambda_rules ' + str(rules))
    # replace_recursion()
    # remove_dead_prikoli()

    logging.info('')
    gre = xy()
    exit()





def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

def proc_gram(tt):
    global vt, vn, rules, orig_rules, s
    fline, *p = [x.strip() for x in tt.split('\n')]
    vt, vn, _, s = map(str.strip, map(rmp, re.split(',(?![^{}]*})', fline[1:])))
    vt, vn = [x.strip() for x in vt.split(',')], [x.strip() for x in vn.split(',')]
    for rule in filter(None, p):
        rule = rule.replace(' ', '')
        f, t = rule.split('->')
        rules[f] = t.split('|')
        for x in rules[f]:
            for c in x:
                if c not in vt+vn+['λ']:
                    raise Exception
    logging.info('VT:' + ' '.join(vt) + ' VN:' + ' '.join(vn) + ' S:' + s)
    logging.info('proc_gram ' + str(rules))
    orig_rules = copy.deepcopy(rules)

def file_dump(s):
    with open('output {}.txt'.format(time.strftime('%d %b %H_%M_%S')), 'w', encoding='utf-8') as f:
        f.write(s)

# Proc

def remove_lambda_rules():
    for k, v in rules.items():
        if 'λ' in v:
            replace_lambda_rule(k)
            if k != s:
                rules[k].remove('λ')

def replace_lambda_rule(nt):
    if nt == s:
        return
    for k, v in rules.items():
        for rule_to in v:
                if nt in rule_to:
                    rules[k].append(rule_to.replace(nt, ''))


def flow(x_nt, trace=[]):
    for x_rt in rules[x_nt]:
        x_rtnt = any(x in x_rt for x in vn) and [x for x in vn if x in x_rt][0]
        logging.info('flow')
        logging.info('x_rt ' + x_rt)
        logging.info('trace ' + str(trace))
        logging.info('x_rtnt ' + str(x_rtnt))
        if x_rtnt:
            x_rtt = x_rt.replace(x_rtnt, '')
            if x_rtnt in ''.join(x + y for x, y in trace):
                # rec
                #print('they might tho')
                #print(x_rtnt == trace[0][1], x_rtnt, trace[0][1])
                if x_rtnt == trace[0][1]:
                    logging.info('flow yep')
                    
                    rules[x_rtnt].append('(' + ''.join(x[0] for x in trace) + x_rtt + ')*')
                    rules[x_rtnt].remove(''.join(trace[1]))
                    
                    logging.info('added ' + '(' + ''.join(x[0] for x in trace) + x_rtt + ')*' + ' to ' + x_rtnt)
                    logging.info('removed ' + ''.join(trace[1]) + ' from ' + x_rtnt)
                    logging.info('rules ' + str(rules))
            else:
                flow(x_rtnt, trace + [(x_rtt, x_rtnt)])
        logging.info('')



def replace_recursion():
    # edge
    for rt in rules[s]:
        if s in rt:
            tmp_x = rt.replace(s, '')
            rules[s].append(f'({tmp_x})*')
            rules[s].remove(rt)
    # else
    flow(s, [('', s)])
    for fr, tr in rules.items():
        if fr != s:
            flow(fr, [('', fr)])
    logging.info('recursion replaced ' + str(rules))


def remove_dead_prikol(dead_neterminal):
    for x_rf, x_rt in rules.items():
        dead_to_me = []
        for x_rule in x_rt:
            if dead_neterminal in x_rule:
                dead_to_me.append(x_rule)
        for i in dead_to_me:
            # print('rem', i)
            rules[x_rf].remove(i)


def remove_dead_prikoli():
    for x_rf, x_rt in rules.items():
        if not x_rt:
            # print('call', x_rf)
            logging.warning('remove dead prikol ' + x_rf)
            remove_dead_prikol(x_rf)


def solve_line(ak, av, meta_rules):
    logging.info('call solve_line ' + ak)
    logging.info(repr(av))
    logging.info('meta ' + str(meta_rules))

    stars = []
    concs = []
    conc_non = {k: [] for k in rules.keys()}

    for i in av:
        for mk, mv in meta_rules.items():
            if mk in i:
                logging.info(repr(mk) + ' in ' + repr(i) + ' so replacing with ' + repr(mv))
                i = i.replace(mk, mv)
        if ak in i:
            logging.info('stars append ' + i.replace(ak, ''))
            stars.append(i.replace(ak, ''))
        else:
            logging.info('solve_line big else ' + i) 
            # concs.append(i)
            if all(x in vt for x in i):
                concs.append(i)
                logging.info('solve_line one symb ' + i) 
            else:
                got_nt = list(filter(lambda x: x in vn, i))[0]
                logging.info('got_nt ' + got_nt)
                conc_non[got_nt].append(i.replace(got_nt, ''))
                logging.info('conc_non ' + repr(conc_non[got_nt]))


    logging.info('solve_line return ')
    logging.info(repr(stars))
    logging.info(repr(concs))
    logging.info(repr(conc_non))
    logging.info('')

    rv = ''
    if len(stars) > 0:
        rv += '('
    rv += ''.join('+'.join(stars))
    if len(stars) > 0:
        rv += ')*'
    
    plust = []
    for k, v in conc_non.items():
        if len(v) == 0:
            continue
        elif len(v) > 1:
            plust.append(k + '(' + '+'.join(v) + ')')
        else:
            plust.append(k + v[0])

    rv += '+'.join(plust + concs)
    logging.info('rv ' + rv)
    return rv


def xy():
    global rules, vt, vn, s

    meta = dict()

    for k, v in sorted(rules.items(), key=lambda x: x[0], reverse=True):
        if k != s:
            meta[k] = solve_line(k, v, meta)

    xsr = solve_line(s, rules[s], meta)
    logging.info('xy return ' + xsr)
    return xsr


def generate_reg_exp(x_nt):
    logging.info('call generate_reg_exp')
    global rules, vt, vn

    final_regex = ''
    final_regex += '('
    if len([x for x in rules[x_nt] if '*' in x]) > 1:
        final_regex += ('(' + ' + '.join([y[:-1] for y in filter(lambda x: '*' in x, rules[x_nt])]) + ')*')
        for xxr in filter(lambda x: '*' in x, rules[x_nt]):
            rules[x_nt].remove(xxr)
    for option in sorted(rules[x_nt], key=lambda x: '*' not in x):
        logging.info('in generate_reg_exp ' + final_regex)
        if '*' in option:
            final_regex += (option + ' ')
        elif any(x in option for x in vn):
            # neterminal est
            final_regex += ('(' + get_t(option) + generate_reg_exp([x for x in vn if x in option][0]) + ')' + ' + ')
        elif all(x in vt for x in option):
            final_regex += (option + ' + ')
    final_regex = final_regex.rstrip('+ ')
    final_regex += ')'

    return final_regex if all(['(' in final_regex, ')' in final_regex, len(final_regex) > 3]) else final_regex[1:-1]


def new_parse_regex(q):
    '''
    ?
    '''
    logging.info('call new_parse_regex')
    # print('call new_parse_regex')
    q = q.replace(' ', '')

    qres = {'n': '+', 'c': []}
    stack = ''
    i = 0
    br = 0
    ab = False

    while i < len(q):
        if qres['n'] == '+':
            if ab:
                stack += q[i]
                if q[i] == '(':
                    br += 1
                elif q[i] == ')':
                    br -= 1
                    if br == 0:
                        ab = False
            elif q[i] != '+' and q[i] != '(':
                stack += q[i]
            elif q[i] == '(':
                stack += q[i]
                br += 1
                ab = True
            elif q[i] == '+':
                qres['c'].append({'n': 'x', 'c': [new_parse_regex(stack)]})
                stack = ''
        elif qres['n'] == 'x':
            ...
        i += 1
    return qres


def parse_reg(xs):
    logging.info('call parse_reg ' + str(xs))
    xs = xs.replace(' ', '')
    # print('call parse_reg', xs)
    stack = []

    open_br = 0
    pr_str = []
    open_or = False
    i = 0
    while i < len(xs):
        # print('i', i, 'c', int(open_or), open_br, pr_str ,xs[i], stack)
        if xs[i] == '(':
            open_br += 1
            pr_str.append('')
        elif xs[i] == ')':
            open_br -= 1
            t = pr_str.pop()
            if not open_or:
                xtt = parse_reg(t)
                if xtt != []:
                    stack.append(xtt)
            else:
                tt = stack.pop()
                stack.append(['+', parse_reg(t), tt])
                open_or = False
            # if open_br == 0:
            #     if not open_or:
            #         stack.append(parse_reg(pr_str))
            #     else:
            #         t = stack.pop()
            #         stack.append(['+', t, parse_reg(pr_str)])
            #         open_or = False
            #     pr_str = ''
        else:
            if xs[i] == '+' and not open_or:
                open_or = True
            elif open_br > 0:
                pr_str[-1] += xs[i]
            elif (xs[i] in vt and not open_or) and ((i+1 < len(xs) and xs[i+1] != '*') or i+1 >= len(xs)):
                stack.append(xs[i])
            elif xs[i] in vt and not open_or and i+1 < len(xs) and xs[i+1] == '*':
                stack.append(['*', xs[i]])
                i += 1
            elif (xs[i] in vt and open_or) and ((i+1 < len(xs) and xs[i+1] != '*') or i+1 >= len(xs)):
                t = stack.pop()
                stack.append(['+', t, xs[i]])
                open_or = False
            elif xs[i] in vt and open_or and i+1 < len(xs) and xs[i+1] == '*':
                t = stack.pop()
                stack.append(['+', t, ['*', xs[i]]])
                open_or = False
                i += 1
            elif xs[i] == '*':
                t = stack.pop()
                stack.append(['*', t])
            elif xs[i] == '+' and open_or:
                raise Exception
        i += 1
        # print('stack', stack)
    # print('stack return')
    return stack


def replace_stars(x_list_reg, star_iter):
    # print('replace stars call', x_list_reg)
    for i, o in enumerate(x_list_reg):
        # print('->', o)
        if type(o) is list:
            if type(o[0]) is list:
                x_list_reg[i] = replace_stars(x_list_reg[i], star_iter)
            elif o[0] == '*':
                if type(o[1]) is list:
                    x_list_reg[i][1] = replace_stars(x_list_reg[i][1], star_iter)
                x_list_reg[i] = [o[1]] * next(star_iter)
            elif o[0] == '+':
                x_list_reg[i] = replace_stars(x_list_reg[i], star_iter)
            elif type(o[0]) is str:
                x_list_reg[i] = replace_stars(x_list_reg[i], star_iter)
    return x_list_reg

def replace_pluses(x_list_reg, plus_iter):
    # print('replace pluses call', x_list_reg)
    for i, o in enumerate(x_list_reg):
        if type(o) is list and o != []:
            if type(o[0]) is list:
                x_list_reg[i] = replace_pluses(x_list_reg[i], plus_iter)
            elif o[0] == '+':
                if type(o[1]) is str and type(o[2]) is str:
                    x_list_reg[i] = o[1 + next(plus_iter)]
                else: #elif type(o[1]) is not str and type(o[2]) is not str:
                    x_list_reg[i] = replace_pluses(x_list_reg[i], plus_iter)[1 + next(plus_iter)]
            elif o[0] == '*':
                x_list_reg[i] = replace_pluses(x_list_reg[i], plus_iter)
            elif type(o[0]) is str:
                x_list_reg[i] = replace_pluses(x_list_reg[i], plus_iter)

            # elif o[0] == '+':
            #     x_list_reg[i] = replace_stars(x_list_reg[i], plus_iter)
    return x_list_reg



def gen_chains_from_parsed_reg(x_reg, maxlen):
    logging.info('call gen_chains_from_parsed_reg')
    # print('gen chains from regex', x_reg)
    chains = set()
    i = 1
    while True:
        logging.info('i ' + str(i))
        new_chains = set()

        for star_variation in itertools.product(* [range(i)] * str(x_reg).count('*')):
            x_reg_nostars = replace_stars(copy.deepcopy(x_reg), iter(star_variation))
            # print('>>>>>', x_reg_nostars)

            for plus_variation in itertools.product(* [range(2)] * str(x_reg_nostars).count('+')):
                x_reg_noplus = replace_pluses(copy.deepcopy(x_reg_nostars), iter(plus_variation))
                # print(x_reg_noplus)

                new_chains.add(''.join(flatten(x_reg_noplus)))

        # cock
        if any(len(x) > maxlen + 5 for x in new_chains) or all(x in chains for x in new_chains):
            chains.update(new_chains)
            break
        chains.update(new_chains)

        i += 1
    return chains

#print(gen_chains_from_parsed_reg([['*', ['+', ['b', 'a'], ['a', 'a']]], ['*', ['b', 'a']], ['b', 'b']], 6))
#exit()

'''
def gen_chains_from_parsed_reg_old(x_reg, maxlen):
    print()
    print('gen chains from regex old')
    chains = set()
    for plus_variation in itertools.product(* [range(2)] * str(x_reg).count('+')):
        print(plus_variation)
        x_reg_noplus = replace_pluses(copy.deepcopy(x_reg), iter(plus_variation))
        print('=======', x_reg_noplus)

        sub_chains = set()
        i = 1
        while True:
            # print(i)
            new_chains = set()
            
            # print('i', i)
            # print(list(itertools.product(* [range(i)] * str(x_reg_noplus).count('*'))))
            for star_variation in itertools.product(* [range(i)] * str(x_reg_noplus).count('*')):
                # print(star_variation)
                x_reg_nostars = replace_stars(copy.deepcopy(x_reg_noplus), iter(star_variation))
                print(x_reg_nostars)
                new_chains.add(''.join(flatten(x_reg_nostars)))

            if any(len(x) > maxlen for x in new_chains) or all(x in sub_chains for x in new_chains):
                sub_chains.update(new_chains)
                break
            sub_chains.update(new_chains)

            i += 1
        chains.update(sub_chains)
    return chains
'''

# with open('input.txt', encoding='utf-8') as f:
#     proc_gram(f.read())

# asd = parse_reg('(aa+bb)*')
# # print('PARSED REG', asd)

# print(
#     gen_chains_from_parsed_reg(asd, 10)
#     )
# exit()


def gen_opt_gram(unc_chain, maxlen, tmp = ''):
    for xgo_symb in unc_chain:
        for pf, pt in orig_rules.items():
            if pf in xgo_symb:
                for pte in pt:
                    yield (tmp := xgo_symb.replace(pf, pte, 1)) if sum(x in vt for x in tmp) <= maxlen else None


def gen_chains_from_gram(s_symb, maxlen):
    xg_res = set()

    for _ in range(9999):
        # print(s_symb)
        to_proc = set()
        for e in gen_opt_gram(s_symb, maxlen):
            if not e:
                continue
            if e == 'λ':
                xg_res.add('')
            if all(x in vt for x in e):
                xg_res.add(e)
            else:
                to_proc.add(e)
        if any(len(x) > maxlen for x in s_symb) or any(len(x) > maxlen for x in xg_res):
            break
        s_symb = to_proc
    return [x for x in xg_res if len(x) <= maxlen]

def get_conc(string):
    logging.info('get_conc call ' + str(string))
    result = []
    
    p = 0
    stack = ''
    for i, c in enumerate(string[1]):
        if p > 0:
            if c == ')':
                p -= 1
                if p > 0:
                    stack += c
                else:
                    ... # ?
            elif c == '(':
                p += 1
                stack += c
            else:
                stack += c
        else:
            if c == '(':
                p += 1
            elif c == ')':
                logging.error('invalid ) in get_conc')
            elif c == '+':
                result.append(('x', stack))
                stack = ''
            else:
                stack += c

    result.append(('x', stack))

    logging.info('get_conc return ' + str(result))

    return result


def get_disc(string):
    logging.info('get_disc call ' + str(string))
    result = []

    p = 0
    stack = ''
    for i, c in enumerate(string[1]):
        if p > 0:
            if c == ')':
                p -= 1
                stack += c

                if p == 0:
                    if i + 1 < len(string[1]) and string[1][i+1] == '*':
                        result.append(('*', stack))
                    else:
                        result.append(('+', stack))
                    stack = ''
                else:
                    ... # stack += c
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
            # bts = bts_ret(bts)
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
        return [x+y for x,y in itertools.product(built[0], built[1])] + list(set([x for x in sorted([''.join(z) for z in itertools.product(*built)] + list(flatten(built))) if len(x) >= minlen and len(x) <= maxlen]))


# xd = parse_reg(out_of_names)
# print('parsed reg', xd, '\n')

# print(parse_reg('(a+(b+a+b)*+a)*'))

# MAX_LEN = 10
# MIN_LEN = 0
# generated_chains = gen_chains_from_parsed_reg(xd, MAX_LEN)
# print([i for i in sorted(generated_chains, key=len) if len(i) <= MAX_LEN and len(i) >= MIN_LEN])
# 
# generated_chains_gram = gen_chains_from_gram(s, MAX_LEN)
# print([i for i in sorted(generated_chains_gram, key=len) if len(i) <= MAX_LEN and len(i) >= MIN_LEN])


class Application(Frame):
    def __init__(self):
        self.root = Tk()
        super().__init__(self.root)
        self.root.geometry("800x600+10+10")
        self.root.title("Вар. 12. Регулярные выражения и грамматики")
        self.pack(fill=BOTH, expand=1)

        self.minl = IntVar(self.root, 0)
        self.maxl = IntVar(self.root, 5)

        self.l1 = Label(self.root, text="Введите грамматику")
        self.l1.place(x=5, y=5)

        self.a1 = Text(self.root, font='consolas')
        self.a1.place(x=5, y=35, height=100, width=300)

        self.l2 = Label(self.root, text="Введите регулярное выражение")
        self.l2.place(x=5, y=140)

        self.a2 = Text(self.root, font='consolas')
        self.a2.place(x=5, y=175, height=25, width=300)

        self.l3 = Label(self.root, text='Сгенерированное рег. выражение')
        self.l3.place(x=5, y=215)

        self.a3 = Text(self.root, font='consolas')
        self.a3.place(x=5, y=250, height=25, width=300)

        self.b1 = Button(self.root, text="1 - Построить регулярное выражение", command=self.b1)
        self.b1.place(x=400, y=32)

        self.b2 = Button(self.root, text="2 - Генерировать цепочки по грамматике", command=self.b2)
        self.b2.place(x=400, y=63)

        self.b3 = Button(self.root, text="3 - Генерировать цепочки по регулярному выражению", command=self.b3)
        self.b3.place(x=400, y=94)

        self.b4 = Button(self.root, text="4 - Генерировать цепочки по вашему регулярному выражению", command=self.b4)
        self.b4.place(x=400, y=125)

        self.b5 = Button(self.root, text="Запись в файл", command=self.b5)
        self.b5.place(x=400, y=158)

        self.b6 = Button(self.root, text="О программе", command=self.b6)
        self.b6.place(x=500, y=158)

        self.s1 = Separator(self.root, orient='horizontal')
        self.s1.place(x=5, y=285, width=790)

        # self.l4 = Label(self.root, text='Цепочки')
        # self.l4.place(x=5, y=290)

        self.lx1 = Label(self.root, text='Цеп. грамматики')
        self.lx1.place(x=5, y=300)

        self.lx2 = Label(self.root, text='Цеп. регулярного выражения')
        self.lx2.place(x=255, y=300)

        self.lx3 = Label(self.root, text='Цеп. вашего выражения')
        self.lx3.place(x=505, y=300)

        self.vsb = Scrollbar(orient="vertical", command=self.OnVsb)
        self.vsb.place(x=760, y=325, height=200, width=15)

        self.lb1 = Listbox(self.root, yscrollcommand=self.vsb.set)
        self.lb2 = Listbox(self.root, yscrollcommand=self.vsb.set)
        self.lb3 = Listbox(self.root, yscrollcommand=self.vsb.set)
        self.lb1.place(x=5, y=325, height=200, width=250)
        self.lb2.place(x=255, y=325, height=200, width=250)
        self.lb3.place(x=505, y=325, height=200, width=250)

        self.lb1.bind("<MouseWheel>", self.OnMouseWheel)
        self.lb2.bind("<MouseWheel>", self.OnMouseWheel)
        self.lb3.bind("<MouseWheel>", self.OnMouseWheel)

        self.l5 = Label(self.root, text='Диапазон')
        self.l5.place(y=195, x=400)

        self.spin1 = Spinbox(self.root, from_=0, to=100, textvariable=self.minl)
        self.spin1.place(y=225, x=400, width=50)
        self.spin2 = Spinbox(self.root, from_=0, to=100, textvariable=self.maxl)
        self.spin2.place(y=225, x=455, width=50)

        # for i in range(100):
        #     self.lb1.insert("end", "item %s" % i)
        #     self.lb2.insert("end", "item %s" % i)
        #     self.lb3.insert("end", "item %s" % i)

        self.gram_chains = []
        self.reg_chains = []

        #with open('input_fixed0.txt', encoding='utf-8') as f:
        #with open('input.txt', encoding='utf-8') as f:
        with open('need_fix.txt', encoding='utf-8') as f:
            self.a1.insert(1.0, f.read()) # fline, *p = [x.strip() for x in f.readlines()]

        self.a3.configure(state='disabled')

        self.root.mainloop()


    def OnMouseWheel(self, event):
        self.lb1.yview("scroll", event.delta, "units")
        self.lb2.yview("scroll", event.delta, "units")
        self.lb3.yview("scroll", event.delta, "units")
        return "break"

    def b1(self):
        tex = self.a1.get(1.0, 'end')
        proc_gram(tex)

        remove_lambda_rules()
        logging.info('remove_lambda_rules ' + str(rules))
        
        # replace_recursion()
        # logging.info('replace_recursion' + str(rules))
        # remove_dead_prikoli()
        # logging.info('remove_dead_prikoli' + str(rules))

        logging.info('')

        # gre = generate_reg_exp(s)
        # generated_reg_exp = gre[1:-1] if all(['(' in gre, ')' in gre, len(gre) > 3]) else gre
        
        generated_reg_exp = xy()
        # generated_reg_exp = proc_ret(generated_reg_exp)

        logging.info('reuslt generate_reg_exp ' + repr(generated_reg_exp))
        
        self.a3.configure(state='normal')
        self.a3.delete(1.0, 'end')
        self.a3.insert(1.0, generated_reg_exp)
        self.a3.configure(state='disabled')


    def b2(self):
        if self.maxl.get() < self.minl.get():
            return
        tex = self.a1.get(1.0, 'end')
        proc_gram(tex)
        generated_chains_gram = gen_chains_from_gram(s, self.maxl.get())
        self.lb1.delete(0, 'end')
        # , key=len
        for x in [i for i in sorted(generated_chains_gram) if len(i) <= self.maxl.get() and len(i) >= self.minl.get()]:
            self.lb1.insert('end', x)
            self.gram_chains.append(x)


    def b3(self):
        if self.maxl.get() < self.minl.get():
            return
        
        tex = self.a3.get(1.0, 'end').strip()
        
        if not tex or (len(tex) == 1 and tex not in vt):
            return
 
        parsed_reg = pNode(tex)
        
        self.lb2.delete(0, 'end')

        final_chains = [i for i in set(class_gen(parsed_reg, self.maxl.get())) if len(i) <= self.maxl.get() and len(i) >= self.minl.get()]
        for x in sorted(final_chains):
            self.lb2.insert('end', x)
            self.reg_chains.append(x)


    def b4(self):
        if self.maxl.get() < self.minl.get():
            return
        tex = self.a2.get(1.0, 'end').strip()
        if not tex or (len(tex) == 1 and tex not in vt):
            return

        parsed_reg = pNode(tex)
        
        self.lb3.delete(0, 'end')

        final_chains = [i for i in set(class_gen(parsed_reg, self.maxl.get())) if len(i) <= self.maxl.get() and len(i) >= self.minl.get()]
        for x in sorted(final_chains):
            self.lb3.insert('end', x)


    def b5(self):
        ox = 'Исходная грамматика:\n' + self.a1.get(1.0, 'end') + 'Регулярное выржаение:\n' + self.a3.get(1.0, 'end') + '\nЦепочки грамматики:\n' + '\n'.join(self.gram_chains) + '\n\nЦепочки регулярного выражения:\n' + '\n'.join(self.reg_chains)
        file_dump(ox)
        logging.info('dump to file')

        logging.info(repr(sorted(self.reg_chains) == sorted(self.gram_chains)))

    def b6(self):
        messagebox.showinfo('О программе', 'Автор: Логинов В.С.\nГруппа: ИП-711\nВариант: 12. Регулярные выражения и грамматики')

    def OnVsb(self, *args):
        self.lb1.yview(*args)
        self.lb2.yview(*args)
        self.lb3.yview(*args)

app = Application()
