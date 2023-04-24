import subprocess, pathlib, os, shutil
import librosa, soundfile
import re
import pykakasi

JULIUS_TMP_DIR = "./julius_segment_tmp"
JULIUS_SEGMENT_SCRIPT_PATH = "/home/murtaza/segmentation-kit/segment_julius.pl"

def format_moras_for_julius(moras):
    text = "".join(moras)
    kks = pykakasi.kakasi()
    hiragana = "".join(entry["hira"] for entry in kks.convert(text))
    hiragana = re.sub(r'([おこごそぞとどのほぼぽもよょろ])(う)', lambda match: match.group(1) + 'ー', hiragana)
    hiragana = re.sub(r'([えけげせぜてでねへべぺめれ])(い)', lambda match: match.group(1) + 'ー', hiragana)
    hiragana = re.sub(r'([お])(お)', lambda match: match.group(1) + 'ー', hiragana)  # おおさか
    # print(hiragana)
    return hiragana

def julius_segment_word(data, sr, moras):
    tmp = pathlib.Path(JULIUS_TMP_DIR)

    data_mono = librosa.to_mono(data)
    resampled = librosa.resample(data_mono, orig_sr=sr, target_sr=16000)
    soundfile.write(tmp/"word.wav", resampled, 16000)
    converted_hiragana = format_moras_for_julius(moras)
    with open(tmp/"word.txt", "w") as f:
        f.write(converted_hiragana)
    
    subprocess.run([
        "/usr/bin/perl",
        JULIUS_SEGMENT_SCRIPT_PATH,
        JULIUS_TMP_DIR
    ], capture_output=True)

    # TODO: error handling

    result = []

    with open(tmp/"word.lab") as f:
        for line in f.readlines():
            start, end, phone = line.strip().split(' ')
            result.append((float(start), phone))
            
    if not result:
        shutil.copyfile(tmp/"word.log", f"julius_logs/{converted_hiragana}.log")
        for path in tmp.glob("*"):
            os.remove(path)
        raise Exception(f"Julius error: see {converted_hiragana}.log")
    
    for path in tmp.glob("*"):
        os.remove(path)
    
    return result

from kana_to_phone_onset import kana_to_phone_onset

def align_onsets_moras(onsets, moras):
    i = 0
    j = 0
    mora_offsets = []
    long_vowels = []
    while i < len(moras):
        if moras[i] == "う" and moras[i-1][-1] in "おこごそぞとどのほぼぽもよょろ" or \
                moras[i] == "い" and moras[i-1][-1] in "えけげせぜてでねへべぺめれ" or \
                moras[i] == "お" and moras[i-1] == "お" or \
                moras[i] == "ー":
            # handle long vowels afterwards
            long_vowels.append(i)
            i += 1

        else:
            # look at the first character of the mora (to simplify all palatalized cases)
            consonant = kana_to_phone_onset[moras[i][0]]
            # we use startswith because the edgecases of things like きょ are not handled
            # we only care about the initial consonant/sound, and this should work in all cases
            while not onsets[j][1].startswith(consonant):
                j += 1
            mora_offsets.append((onsets[j][0], moras[i]))
            i += 1
            j += 1

    mora_offsets.append((onsets[-1][0], "$")) # silence at end

    for long_vowel_i in long_vowels:
        hiragana_vowel = moras[long_vowel_i]
        # heuristic: long vowel is halfway between neighboring syllables
        start = (mora_offsets[long_vowel_i - 1][0] + mora_offsets[long_vowel_i][0]) / 2
        mora_offsets.insert(long_vowel_i, (start, hiragana_vowel))

    assert(len(mora_offsets) == len(moras) + 1)

    return mora_offsets

def get_syllables_start_end_julius(data, sr, moras):

    onsets = julius_segment_word(data, sr, moras)
    mora_onsets = align_onsets_moras(onsets, moras)
    # print(mora_onsets)

    for i in range(len(mora_onsets) - 1):
        start_t, end_t = mora_onsets[i][0], mora_onsets[i+1][0]
        start_s, end_s = round(start_t * sr), round(end_t * sr)
        yield mora_onsets[i][1], start_s, end_s