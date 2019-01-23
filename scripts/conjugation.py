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

V2E = {
    "あ": "え", "い": "え", "う": "え", "え": "え", "お": "え",
    "ぁ": "ぇ", "ぃ": "ぇ", "ぅ": "ぇ", "ぇ": "ぇ", "ぉ": "ぇ",
    "か": "け", "き": "け", "く": "け", "け": "け", "こ": "け",
    "が": "げ", "ぎ": "げ", "ぐ": "げ", "げ": "げ", "ご": "げ",
    "さ": "せ", "し": "せ", "す": "せ", "せ": "せ", "そ": "せ",
    "た": "て", "ち": "て", "つ": "て", "っ": "て", "て": "て", "と": "て",
    "だ": "で", "ぢ": "で", "づ": "で", "で": "で", "ど": "で",
    "な": "ね", "に": "ね", "ぬ": "ね", "ね": "ね", "の": "ね",
    "は": "へ", "ひ": "へ", "ふ": "へ", "へ": "へ", "ほ": "へ",
    "ば": "べ", "び": "べ", "ぶ": "べ", "べ": "べ", "ぼ": "べ",
    "ぱ": "ぺ", "ぴ": "ぺ", "ぷ": "ぺ", "ぺ": "ぺ", "ぽ": "ぺ",
    "ま": "め", "み": "め", "む": "め", "め": "め", "も": "め",
    "や": "え", "ゆ": "え", "よ": "え", "ゃ": "ぇ", "ゅ": "ぇ", "ょ": "ぇ",
    "ら": "れ", "り": "れ", "る": "れ", "れ": "れ", "ろ": "れ",
    "わ": "え", "を": "え", "ん": "え",
    "ア": "エ", "イ": "エ", "ウ": "エ", "エ": "エ", "オ": "エ",
    "ァ": "ェ", "ィ": "ェ", "ゥ": "ェ", "ェ": "ェ", "ォ": "ェ",
    "カ": "ケ", "キ": "ケ", "ク": "ケ", "ケ": "ケ", "コ": "ケ",
    "ガ": "ゲ", "ギ": "ゲ", "グ": "ゲ", "ゲ": "ゲ", "ゴ": "ゲ",
    "サ": "セ", "シ": "セ", "ス": "セ", "セ": "セ", "ソ": "セ",
    "タ": "テ", "チ": "テ", "ツ": "テ", "ッ": "テ", "テ": "テ", "ト": "テ",
    "ダ": "デ", "ヂ": "デ", "ヅ": "デ", "デ": "デ", "ド": "デ",
    "ナ": "ネ", "ニ": "ネ", "ヌ": "ネ", "ネ": "ネ", "ノ": "ネ",
    "ハ": "ヘ", "ヒ": "ヘ", "フ": "ヘ", "ヘ": "ヘ", "ホ": "ヘ",
    "バ": "ベ", "ビ": "ベ", "ブ": "ベ", "ベ": "ベ", "ボ": "ベ",
    "パ": "ペ", "ピ": "ペ", "プ": "ペ", "ペ": "ペ", "ポ": "ペ",
    "マ": "メ", "ミ": "メ", "ム": "メ", "メ": "メ", "モ": "メ",
    "ヤ": "エ", "ユ": "エ", "ヨ": "エ", "ャ": "ェ", "ュ": "ェ", "ョ": "ェ",
    "ラ": "レ", "リ": "レ", "ル": "レ", "レ": "レ", "ロ": "レ",
    "ワ": "エ", "ヲ": "エ", "ン": "エ",
}

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
            if ending.startswith("-e"):
                raise LookupError("cannot reconstruct stem from -e form because of loss of information")
            if self.midasi.endswith(ending):
                self.eidx = eidx
                # assumption that '語幹' has a zero-length ending
                self.stem = self.midasi[:len(self.midasi) - len(ending)]
                return self.stem
        raise LookupError("inconsistent ending")

    def transform(self, tform):
        self.get_stem()
        ending = self.cmap.type2form[self.ctype][tform][self.eidx]
        if ending.startswith("-e"):
            ending = ending[2:]
            if self.stem[-1] in V2E:
                stem = self.stem[:-1] + V2E[self.stem[-1]]
            else:
                stem = self.stem
            return stem + ending
        else:
            return self.stem + ending

    def get_all_forms(self):
        self.get_stem()
        forms = {}
        form_list = self.cmap.type2form[self.ctype]
        for cform in form_list.keys():
            forms[cform] = self.transform(cform)
        return forms

if __name__ == "__main__":
    katuyou_fp = "../grammar/JUMAN.katuyou"
    katuyou_dic = KatuyouDic(open(katuyou_fp).read())
    inf = Conjugation(katuyou_dic, 'だ', '判定詞', '基本形')
    print(inf.transform('デス列基本形'))

    inf = Conjugation(katuyou_dic, 'きた', 'カ変動詞来', 'タ形')
    print(inf.transform('意志形'))
    print(inf.get_all_forms())

    inf = Conjugation(katuyou_dic, '来る', 'カ変動詞来', '基本形')
    print(inf.transform('基本連用形'))
    print(inf.get_all_forms())

    inf = Conjugation(katuyou_dic, 'すごい', 'イ形容詞アウオ段', '基本形')
    print(inf.transform('エ基本形'))
    print(inf.get_all_forms())

    ## failure cases
    # inf = Conjugation(katuyou_dic, 'です', '判定詞', '基本形')
    # print(inf.get_stem())

    # inf = Conjugation(katuyou_dic, 'です', '判定', '基本形2')
    # print(inf.get_stem())

    # inf = Conjugation(katuyou_dic, 'です', '判定詞', '基本形2')
    # print(inf.get_stem())

    # inf = Conjugation(katuyou_dic, 'すげえ', 'イ形容詞アウオ段', 'エ基本形')
    # print(inf.transform('基本形'))
