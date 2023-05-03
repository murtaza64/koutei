from word_map import load_word_map
from julius_interface import get_syllables_start_end_julius
import librosa
from scipy.signal import find_peaks
import statsmodels.api as sm
import matplotlib as plt
import numpy as np
import warnings
from typing import List, Tuple

word_map = load_word_map()

def get_first_strong_peak(x, label=None, graph=False):
    acorr = sm.tsa.acf(x, nlags=2000)
    peaks = find_peaks(acorr)[0]
    
    if graph:
        plt.plot(acorr, label=label)
        L = plt.legend()
        plt.setp(L.texts, family='TakaoMincho')
    
    peaks = [peak for peak in peaks if peak > 20] # filter out low offest (high frequency) peaks
    if not peaks:
        return -1, 0
    max_peak = max(peaks, key=lambda p: acorr[p])
    return max_peak, acorr[max_peak]


INTERVAL_SAMPLES = 100
WINDOW_SAMPLES = 800
def get_pitches_fine_grained(data, sample_rate):
    for chunk_start in range(0, len(data), INTERVAL_SAMPLES):
        chunk = data[chunk_start:chunk_start+WINDOW_SAMPLES]
        strong_peak, acorr = get_first_strong_peak(chunk)
        if strong_peak > 20 \
                and 50 < sample_rate / strong_peak < 500 \
                and acorr > 0.5:
            yield chunk_start, round(sample_rate / strong_peak, 1)


def get_avg_syllable_pitches(wav_path, moras) -> List[Tuple[str, float]]:
    data, sr = librosa.load(wav_path)
    onsets_and_pitches = list(get_pitches_fine_grained(data, sr))
    sylls = list(get_syllables_start_end_julius(data, sr, moras))
    # print(onsets_and_pitches)
    # print(sylls)
    i = 0 
    # start at beginning of first syllable
    while onsets_and_pitches[i][0] < sylls[0][1]:
        i += 1
    avg_pitches = []
    for mora, syll_s, syll_e in sylls:
        pitches = []
        while i < len(onsets_and_pitches) and onsets_and_pitches[i][0] < syll_e:
            pitches.append(onsets_and_pitches[i][1])
            i += 1

        try:
            avg_pitch = sum(pitches) / len(pitches)
        except ZeroDivisionError:
            # if no pitch detected, just use previous pitch
            warnings.warn(f"{wav_path}: No pitch detected for {mora}, using same pitch as previous syllable")
            if avg_pitches:
                avg_pitch = avg_pitches[-1][1]
            else:
                avg_pitch = 200 #TODO

        avg_pitches.append((mora, avg_pitch))
    return avg_pitches


def pitch_contour_similarity(expected: List[float], pronounced: List[float], nucleus_idx: int) -> float:

    assert len(expected) == len(pronounced)
    score = 0
    # extremal pitches are in correct position
    if np.argmin(expected) == np.argmin(pronounced):
        score += 10
        print("\t+10 min pitch in correct position")
    if np.argmax(pronounced) == nucleus_idx:
        score += 10
        print("\t+10 max pitch in accent nucleus position")
    
    # accent nucleus is higher than its successor
    if nucleus_idx < len(expected)-1:
        if pronounced[nucleus_idx] > pronounced[nucleus_idx + 1]:
            score += 10
            print("\t+10 accent nucleus higher than successor")
    # # accent nucleus is higher than its predecessor
    # if nucleus_idx > 0:
    #     if pronounced[nucleus_idx] > pronounced[nucleus_idx - 1]:
    #         score += 10
    
    #adjacent pitch relations are correct
    normalizer = len(expected) - 1
    for i in range(len(expected) - 1):
        if expected[i+1] > expected[i] and pronounced[i+1] > pronounced[i]:
            score += 40 / normalizer
            print(f"\t+{40/normalizer} {i+1} higher than {i}")
        if expected[i+1] < expected[i] and pronounced[i+1] < pronounced[i]:
            score += 40 / normalizer
            print(f"\t+{40/normalizer} {i+1} lower than {i}")
        if expected[i+1] == expected[i]:
            # give score for closeness in pitch up to 10% difference
            # quadratic so that differences closer to 0 are rewarded
            # 5% delta gets 75% of points
            # 1% gets 99%
            l, r = pronounced[i], pronounced[i+1]
            delta = abs(l - r) / max(l, r)
            bonus = max(0, (1 - 10*delta**2)) * 40 / normalizer
            score += bonus
            print(f"\t+{bonus} {i+1} should be close to {i}: {delta}")
    return score

if __name__ == "__main__":
    for word, data in word_map.items():
        wav_path = f"../../jpp/public/audio/{data['category']}/{word}.wav"
        syll_pitches = get_avg_syllable_pitches(wav_path, data["moras"])
        pitches_only = [s[1] for s in syll_pitches]
        expected_pitches = data["pitches"]
        nucleus_idx = data["peak"]
        print(word, pitches_only, pitch_contour_similarity(expected_pitches, pitches_only, nucleus_idx))