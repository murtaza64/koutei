"""
This file contains approximate mappings from hiragana to phones emitted by julius. The mapping
is used to align morae (in terms of hiragana characters) to the segmentation output of julius,
which is done by `align_onsets_kana`.

They are not exact, for example きょ will be emitted as /ky o/, but this file maps き to "k",
so these mappings should be used with `startswith`.
"""

kana_to_phone_onset = {
    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",

    "か": "k",
    "き": "k",
    "く": "k",
    "け": "k",
    "こ": "k",

    "た": "t",
    "ち": "t",
    "つ": "t",
    "て": "t",
    "と": "t",

    "さ": "s",
    "し": "sh",
    "す": "s",
    "せ": "s",
    "そ": "s",

    "な": "n",
    "に": "n",
    "ぬ": "n",
    "ね": "n",
    "の": "n",

    "は": "h",
    "ひ": "h",
    "ふ": "f",
    "へ": "h",
    "ほ": "h",

    "ま": "m",
    "み": "m",
    "む": "m",
    "め": "m",
    "も": "m",

    "や": "y",
    "ゆ": "y",
    "よ": "y",

    "ら": "r",
    "り": "r",
    "る": "r",
    "れ": "r",
    "ろ": "r",

    "わ": "w",
    "を": "w",

    "ん": "N",

    "が": "g",
    "ぎ": "g",
    "ぐ": "g",
    "げ": "g",
    "ご": "g",

    "ざ": "z",
    "じ": "j",
    "ず": "z",
    "ぜ": "z",
    "ぞ": "z",

    "だ": "d",
    "ぢ": "j",
    "づ": "z",
    "で": "d",
    "ど": "d",

    "ば": "b",
    "び": "b",
    "ぶ": "b",
    "べ": "b",
    "ぼ": "b",

    "ぱ": "p",
    "ぴ": "p",
    "ぷ": "p",
    "ぺ": "p",
    "ぽ": "p"
}

# add katakana equivalents

import pykakasi
kks = pykakasi.kakasi()
for key, val in list(kana_to_phone_onset.items()):
    kana_to_phone_onset[kks.convert(key)[0]["kana"]] = val