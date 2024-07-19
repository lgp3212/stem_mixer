import json
import os
import librosa
import numpy as np
import math

import mix

DEFAULT_SR = 22050

def extraction(stem_file_path, **kwargs):

    # returning metadata object might be better, writing somewhere else
    # issue w passing kwargs each time is with each iteration this resets to none and goes through whole process again
    # talk to giovana about using kwargs

    json_file_path  = os.path.splitext(stem_file_path)[0] + ".json"

    if not os.path.exists(json_file_path):

        metadata = kwargs.copy()

        # duration refers to the mixture duration, therefore we don't need it.
        metadata.pop("duration", None)
        metadata.pop("track_files", None)
        metadata.pop("duration", None)
        metadata.pop("n_mixtures", None)
        metadata.pop("n_harmonic", None)
        metadata.pop("n_percussive", None)
        metadata.pop("n_stems", None)

        if metadata["tempo"] is None:
            tempo = get_tempo(stem_file_path) # if tempo is none, we extract it
            metadata["tempo"] = tempo # updating metadata

        if metadata["sound_class"] is None:
            sound_class = percussive_harmonic(stem_file_path) # if sound class is none, we extract it
            metadata["sound_class"] = sound_class # updating metadata

        metadata["tempo bin"] = math.ceil(metadata["tempo"] / 5) * 5 # adding tempo-bin to metadata

        with open(json_file_path, "w") as json_file:
            json.dump(metadata, json_file, indent=4)
            print("json file created")

def get_tempo(stem_path): 

    try:
        audio_file, sr = librosa.load(stem_path, sr=DEFAULT_SR, mono=True)
        tempo, _ = librosa.beat.beat_track(y=audio_file, sr=sr)
        tempo = float(tempo[0])

    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return tempo

def percussive_harmonic(stem_path): # in the works: extracting percussive / harmonic component if not provided
    try:
        audio_file, sr = librosa.load(stem_path, sr=DEFAULT_SR, mono=True)
        audio_norm = librosa.util.normalize(audio_file)
        harmonic, percussive = librosa.effects.hpss(audio_norm)

        print(stem_path)

        harmonic_energy = np.sqrt(np.mean(np.square(harmonic)))
        print("harmonic energy rmse ", harmonic_energy)
      
        percussive_energy = np.sqrt(np.mean(np.square(percussive)))
        print("percussive energy rmse ",percussive_energy)
      

        percent_difference = abs(harmonic_energy - percussive_energy) / ((harmonic_energy + percussive_energy) / 2)
        print(percent_difference)

        threshold = 0.50 # 50% THRESHOLD, subject to change

        if percent_difference > threshold:
            result = "percussive" if percussive_energy > harmonic_energy else "harmonic"
        else:
            #result = None; changed bc if none then it will just keep looping 
            result = "undetermined"

        print(result)
        print("")

    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return result

