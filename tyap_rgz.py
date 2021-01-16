# λ
from tkinter import Tk, Text, BOTH, W, N, E, S, Scrollbar, Listbox, IntVar, messagebox
from tkinter.ttk import Frame, Button, Label, Style, Separator, Spinbox

import re
import os
import copy
import time
import itertools
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    handlers=[
        logging.FileHandler('logs\\log ' + time.strftime('%d %b %H_%M_%S') + '.txt'),
        logging.StreamHandler()
    ]
)

rmp = lambda x: x.replace('{', '').replace('}', '').replace('(', '').replace(')', '')


orig_rules = dict()
rules = dict()
vt = list()
vn = list()
s = str()


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


def unp(string):

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


def class_gen(tree_obj, burn):
    logging.info('call class_gen ' + str(tree_obj))
    if type(tree_obj) is sNode:
        # ['c', 'd'] -> ['c', 'd', 'cd', 'dc', 'cc', 'dd', ...]
        # ['ab'] -> ['ab', 'abab', ...]
        z = []
        for child in tree_obj.childs:
            z += class_gen(child, burn)
        if len(z) == 1:
            package = ['']
            for i in range(burn + 1):
                package += [z[0] * i]
            return package
        else:
            # STRING FACTORY
            package = ['']
            for i in range(burn):
                package += [''.join(x) for x in itertools.product(z, repeat=i)]
            return package
            # return ['', 'c', 'd', 'cc', 'dd', 'cd', 'dc']
    elif type(tree_obj) is pNode:
        # ['a'], ['b', 'bc' ,'bd', ...], ['ef'] -> ['a', 'b', 'bc' ,'bd', ..., 'ef']
        z = []
        for child in tree_obj.childs:
            z += class_gen(child, burn)
        # logging.info('class_gen(pNode) return ' + str(z))
        return z
    elif type(tree_obj) is xNode:
        # ['b'], ['', 'c', 'd', 'cc', 'cd', ...] -> ['b', 'bc' ,'bd', ...]
        z = [class_gen(child, burn) for child in tree_obj.childs]
        y = []
        # logging.info('z ' + str(z)) # <----
        for t in itertools.product(*z):
            y.append(''.join(t))
        # logging.info('class_gen(xNode) return ' + str(y))
        return y

    elif type(tree_obj) is str:
        # 'a' -> ['a']
        return [tree_obj]


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


def gen_opt_gram(unc_chain, maxlen, tmp = ''):
    for xgo_symb in unc_chain:
        for pf, pt in orig_rules.items():
            if pf in xgo_symb:
                for pte in pt:
                    yield (tmp := xgo_symb.replace(pf, pte, 1)) if sum(x in vt for x in tmp) <= maxlen else None


def gen_chains_from_gram(s_symb, maxlen):
    xg_res = set()

    for _ in range(9999):
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

        self.gram_chains = []
        self.reg_chains = []
        self.ure_chains = []

        with open('input.txt', encoding='utf-8') as f:
            self.a1.insert(1.0, f.read())

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

        generated_reg_exp = xy()

        logging.info('reuslt xy ' + repr(generated_reg_exp))
        
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
            self.ure_chains.append(x)


    def b5(self):
        ox = 'Исходная грамматика:\n' + self.a1.get(1.0, 'end') + \
        'Регулярное выржаение:\n' + self.a3.get(1.0, 'end') + \
        '\nЦепочки грамматики:\n' + '\n'.join(self.gram_chains) + \
        '\n\nЦепочки регулярного выражения:\n' + '\n'.join(self.reg_chains) + \
        '\n\nЦепочки вашего регулярного выражения:\n' + '\n'.join(self.ure_chains)
        file_dump(ox)
        logging.info('dump to file')

    def b6(self):
        messagebox.showinfo('О программе', 'Автор: Логинов В.С.\nГруппа: ИП-711\nВариант: 12. Регулярные выражения и грамматики')

    def OnVsb(self, *args):
        self.lb1.yview(*args)
        self.lb2.yview(*args)
        self.lb3.yview(*args)

app = Application()
