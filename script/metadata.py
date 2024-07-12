import json
import os

def extraction(path_to_stem, tempo, instrument_name, key, sound_class):

	# whenever i add text description here get indentation error, it's in google doc for now

    if (path_to_stem.endswith(".wav") or path_to_stem.endswith(".mp3")) and not path_to_stem.endswith(".json"):
        json_name = path_to_stem[0:len(path_to_stem)-4]
    else:
        json_name = None

    metadata = {}
    metadata["tempo"] = tempo
    metadata["instrument_name"] = instrument_name
    metadata["key"] = key
    metadata["sound_class"] = sound_class

    stems = os.path.join(path_to_stem, "..")
    json_file_path = os.path.join(stems, f"{json_name}.json")

    if not os.path.exists(json_file_path):
        with open(json_file_path, "w") as json_file:
            json.dump(metadata, json_file, indent=4)


def get_wav_from_json(path_to_stems, file_name): # useful for getting tempo, instrument name, etc
    for file in os.listdir(path_to_stems):
        if file_name in file and not file.endswith(".json"):
            audio_path = file
    return audio_path
  