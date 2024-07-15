import json
import os
import librosa
import mix
import numpy as np

def extraction(stem_file_path, **kwargs):

    # returning metadata object might be better, writing somewhere else

    basename = os.path.splitext(stem_file_path)[0]
    json_file_path = basename + ".json"

    metadata = kwargs.copy()
    # duration refers to the mixture duration, therefore we don't need it.
    metadata.pop("duration", None)
    metadata.pop("track_files", None)

    if metadata["tempo"] is None:
        print("tempo is None. calculating...")
        metadata["tempo"] = get_tempo(stem_file_path, sr=kwargs["sr"])

    # TODO: should we save this here or somewhere else?
    if not os.path.exists(json_file_path):
        with open(json_file_path, "w") as json_file:
            json.dump(metadata, json_file, indent=4)
            print("json file created")


def get_tempo(stem_path, sr):

    try:
        audio_file, sr = librosa.load(stem_path, sr=sr, mono=True)
        tempo, _ = librosa.beat.beat_track(y=audio_file, sr=sr)
        tempo = float(tempo[0])

    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return tempo

def percussive_harmonic(stem_path, sr):
    try:
        audio_file, sr = librosa.load(stem_path, sr=sr, mono=True)
        audio_norm = librosa.util.normalize(audio_file)
        harmonic, percussive = librosa.effects.hpss(audio_norm)

        print(stem_path)

        harmonic_energy = abs(np.mean(harmonic))
        print("harmonic energy ", harmonic_energy)
        percussive_energy = abs(np.mean(percussive))
        print("percussive energy ",percussive_energy)

        percent_difference = abs(harmonic_energy - percussive_energy) / ((harmonic_energy + percussive_energy) / 2)
        print(percent_difference)

        threshold = 0.15 # 30% THRESHOLD

        if percent_difference > threshold:
            result = "percussive" if percussive_energy > harmonic_energy else "harmonic"
        else:
            result = None

        print(result)
        print("")

    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")

