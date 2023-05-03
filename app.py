from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from base64 import b64decode
import subprocess
from word_map import word_map
from koutei import get_avg_syllable_pitches, pitch_contour_similarity

app = Flask(__name__)
CORS(app)

# @app.route("/check", methods=["OPTIONS"])
# def cors_preflight():
#     response = make_response()
#     response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
#     response.headers.add("Access-Control-Allow-Headers", "*")
#     return response


@app.route("/check", methods=["POST"])
def check_pitch():
    # print(request.json)
    audio = str(request.json["audio"])
    audio = audio.split(",")[1]
    audio = b64decode(audio)
    # with open("audio.webm", "wb") as f:
    #     f.write(audio)

    p = subprocess.run(["ffmpeg", "-y", "-i", "-", "-vn", "audio.wav"], input=audio, capture_output=True)
    if p.returncode != 0:
        print("ffmpeg:", p.returncode)
        print(p.stdout)
        print(p.stderr)
        return {"error": "ffmpeg failed to convert audio"}, 500
    wav_path = "audio.wav"
    try:
        word_data = word_map[request.json["word"]]
    except KeyError:
        return {"error": "word not found in word map"}, 404

    syll_pitches = get_avg_syllable_pitches(wav_path, word_data["moras"])
    print(syll_pitches)
    pitches_only = [s[1] for s in syll_pitches]
    score = pitch_contour_similarity(word_data["pitches"], pitches_only, word_data["peak"])

    response = jsonify({"score": score})
    # response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    return response
