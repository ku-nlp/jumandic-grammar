#!/usr/bin/env python3
# coding:utf-8

import sys
from sexp import SParser

class KatuyouDic(object):
    def __init__(self, katuyou_dat):
        self.type2form = {} # type -> form -> ending_list
        
        sp = SParser()
        for s_exp in sp.parse(katuyou_dat):
            ctype = s_exp[0]
            self.type2form[ctype] = {}
            if len(s_exp) > 1:
                # カ変動詞来 has two endings
                for cform, *ending_list in s_exp[1]:
                    ending_list = ['' if s == '*' else s for s in ending_list]
                    self.type2form[ctype][cform] = ending_list

class Conjugation(object):
    def __init__(self, katuyou_dic, midasi, ctype, cform):
        self.cmap = katuyou_dic
        self.midasi = midasi
        self.ctype = ctype
        self.cform = cform
        self.eidx = 0 # カ変動詞来 has two endings

        if self.ctype not in self.cmap.type2form:
            raise ValueError("undefined ctype {}".format(self.ctype))
        if self.cform not in self.cmap.type2form[self.ctype]:
            raise ValueError("undefined ctype-cform pair {} {}".format(self.ctype, self.cform))

    def get_stem(self):
        if hasattr(self, 'stem'):
            return self.stem
        form_list = self.cmap.type2form[self.ctype]
        for eidx, ending in enumerate(form_list[self.cform]):
            if self.midasi.endswith(ending):
                self.eidx = eidx
                # assumption that '語幹' has a zero-length ending
                self.stem = self.midasi[:len(self.midasi) - len(ending)]
                return self.stem
        raise LookupError("inconsistent ending")

    def transform(self, tform):
        self.get_stem()
        return self.stem + self.cmap.type2form[self.ctype][tform][self.eidx]

    def get_all_forms(self):
        self.get_stem()
        forms = {}
        form_list = self.cmap.type2form[self.ctype]
        for cform in form_list.keys():
            form = self.stem + form_list[cform][self.eidx]
            forms[cform] = form
        return forms

if __name__ == "__main__":
    katuyou_fp = "../grammar/JUMAN.katuyou"
    katuyou_dic = KatuyouDic(open(katuyou_fp).read())
    inf = Conjugation(katuyou_dic, 'だ', '判定詞', '基本形')
    print(inf.transform('デス列基本形'))

    inf = Conjugation(katuyou_dic, 'きた', 'カ変動詞来', 'タ形')
    print(inf.transform('意志形'))

    inf = Conjugation(katuyou_dic, '来る', 'カ変動詞来', '基本形')
    print(inf.transform('基本連用形'))
    print(inf.get_all_forms())

    ## failure cases
    # inf = Conjugation(katuyou_dic, 'です', '判定詞', '基本形')
    # print(inf.get_stem())

    # inf = Conjugation(katuyou_dic, 'です', '判定', '基本形2')
    # print(inf.get_stem())

    # inf = Conjugation(katuyou_dic, 'です', '判定詞', '基本形2')
    # print(inf.get_stem())
