# λ
from tkinter import Tk, Text, BOTH, W, N, E, S, Scrollbar, Listbox, IntVar
from tkinter.ttk import Frame, Button, Label, Style, Separator, Spinbox

import re
import os
import copy
import itertools
from collections.abc import Iterable

# sys.stdout = open('file', 'w')

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




# checks
pass # TODO

# utils

get_t = lambda x: ''.join(i for i in x if i in vt)

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
                if c not in vt+vn:
                    raise Exception
    print('VT:', *vt, '\nVN:', *vn, '\nS:', s)
    print(rules)
    orig_rules = copy.deepcopy(rules)

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


# remove_lambda_rules()
# print(rules, '\n')

def flow(x_nt, trace=[]):
    for x_rt in rules[x_nt]:
         x_rtnt = any(x in x_rt for x in vn) and [x for x in vn if x in x_rt][0]
         print('rule in flow', x_rt)
         print('flow', x_rtnt, 'trace:', trace)
         if x_rtnt:
            x_rtt = x_rt.replace(x_rtnt, '')
            if x_rtnt in ''.join(x + y for x, y in trace):
                # rec
                #print('they might tho')
                #print(x_rtnt == trace[0][1], x_rtnt, trace[0][1])
                if x_rtnt == trace[0][1]:
                    print('flow YEP')
                    # proc here
                    rules[x_rtnt].append('(' + ''.join(x[0] for x in trace) + x_rtt + ')*')
                    # remove vvhod na vtoroi crug
                    # print(rules[trace[-1][1]])
                    # print(trace)
                    rules[x_rtnt].remove(''.join(trace[1]))
                    # rules[trace[-1][1]].remove(x_rt)                
            else:
                flow(x_rtnt, trace + [(x_rtt, x_rtnt)])



def replace_recursion():
    flow(s, [('', s)])
    for fr, tr in rules.items():
        if fr != s:
            flow(fr, [('', fr)])
    print('rec replaced', rules)

# replace_recursion()
# print(json.dumps(rules, indent=4, sort_keys=False))
# print(rules)

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
            print('call', x_rf)
            remove_dead_prikol(x_rf)

# remove_dead_prikoli()
# print(rules)


def generate_reg_exp(x_nt):
    global rules, vt, vn
    print('gen_reg', rules, x_nt)
    # print('vn in func', vn)
    # print('x_nt', x_nt)
    # print('rules in func', rules)
    final_regex = ''
    final_regex += '('
    if len([x for x in rules[x_nt] if '*' in x]) > 1:
        # [:-1]
        final_regex += ('(' + ' + '.join([y[:-1] for y in filter(lambda x: '*' in x, rules[x_nt])]) + ')*')
        for xxr in filter(lambda x: '*' in x, rules[x_nt]):
            rules[x_nt].remove(xxr)
    for option in sorted(rules[x_nt], key=lambda x: '*' not in x):
        # print('rabotaem', final_regex)
        if '*' in option:
            final_regex += (option + ' ')
        elif any(x in option for x in vn):
            # neterminal est
            final_regex += ('(' + get_t(option) + generate_reg_exp([x for x in vn if x in option][0]) + ')' + ' + ')
        elif all(x in vt for x in option):
            final_regex += (option + ' + ')
    final_regex = final_regex.rstrip('+ ')
    final_regex += ')'
    

    #final_regex += ('(' + 
    #        ' '.join(x for x in tr if '*' in x) + ' ' + 
    #        ' + '.join(get_t(x) for x in tr if '*' not in x) + 
    #        ')')

    print(final_regex)
    # return final_regex if len(final_regex) > 1 else final_regex[1:-1]
    return final_regex if all(['(' in final_regex, ')' in final_regex, len(final_regex) > 3]) else final_regex[1:-1]

# out_of_names = generate_reg_exp(s)[1:-1]
# print(out_of_names)

def parse_reg(xs):
    xs = xs.replace(' ', '')
    print('call parse_reg', xs)
    stack = []

    open_br = 0
    pr_str = []
    open_or = False
    i = 0
    while i < len(xs):
        print('i', i, 'c', int(open_or), open_br, pr_str ,xs[i], stack)
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
    print('stack return')
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
    print('gen chains from regex', x_reg)
    chains = set()
    i = 1
    while True:
        print('i', i)
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

def gen_chains_from_parsed_reg_old(x_reg, maxlen):
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
        self.root.title("RGZ KEK")
        self.pack(fill=BOTH, expand=1)

        self.minl = IntVar(self.root, 0)
        self.maxl = IntVar(self.root, 6)

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

        self.s1 = Separator(self.root, orient='horizontal')
        self.s1.place(x=5, y=285, width=790)

        self.l4 = Label(self.root, text='Цепочки')
        self.l4.place(x=5, y=290)

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
        self.l5.place(y=175, x=400)

        self.spin1 = Spinbox(self.root, from_=0, to=100, textvariable=self.minl)
        self.spin1.place(y=205, x=400, width=50)
        self.spin2 = Spinbox(self.root, from_=0, to=100, textvariable=self.maxl)
        self.spin2.place(y=205, x=455, width=50)

        # for i in range(100):
        #     self.lb1.insert("end", "item %s" % i)
        #     self.lb2.insert("end", "item %s" % i)
        #     self.lb3.insert("end", "item %s" % i)

        with open('input.txt', encoding='utf-8') as f:
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
        replace_recursion()
        # replace_recursion()
        remove_dead_prikoli()

        gre = generate_reg_exp(s)
        generated_reg_exp = gre[1:-1] if all(['(' in gre, ')' in gre, len(gre) > 3]) else gre
        print('generate_reg_exp', generated_reg_exp)
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


    def b3(self):
        if self.maxl.get() < self.minl.get():
            return
        tex = self.a3.get(1.0, 'end')
        if not tex or (len(tex) == 1 and tex not in vt):
            return
        xd = parse_reg(tex)
        print('parsed reg', xd)

        generated_chains = gen_chains_from_parsed_reg(xd, self.maxl.get())
        self.lb2.delete(0, 'end')
        # , key=len
        for x in [i for i in sorted(generated_chains) if len(i) <= self.maxl.get() and len(i) >= self.minl.get()]:
            self.lb2.insert('end', x)


    def b4(self):
        if self.maxl.get() < self.minl.get():
            return
        tex = self.a2.get(1.0, 'end')
        if not tex or (len(tex) == 1 and tex not in vt):
            return
        xd = parse_reg(tex)
        print('parsed reg', xd)

        generated_chains = gen_chains_from_parsed_reg(xd, self.maxl.get())
        self.lb3.delete(0, 'end')
        # , key=len
        for x in [i for i in sorted(generated_chains) if len(i) <= self.maxl.get() and len(i) >= self.minl.get()]:
            self.lb3.insert('end', x)



    def OnVsb(self, *args):
        self.lb1.yview(*args)
        self.lb2.yview(*args)
        self.lb3.yview(*args)

app = Application()
