import json
import os
import librosa

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
            print("json file created")


def get_wav_from_json(path_to_stems, file_name): # useful for getting tempo, instrument name, etc
    for file in os.listdir(path_to_stems):
        if file_name in file and not file.endswith(".json"):
            audio_path = file
    return audio_path


def set_tempo(data_home, sr):
	print("ENTERING SET TEMPO")
	path_to_stems = os.path.join(data_home, "stems")
	json_files = [file for file in os.listdir(path_to_stems) if file.endswith(".json") and not file.startswith(".")]
	print("Trying to see if it 'sees' first json file:",json_files)

	for json_file in json_files:
		print(json_file)
		file_path = os.path.join(path_to_stems, json_file)
		print(file_path)
		file_name = os.path.basename(file_path)
		file_name = os.path.splitext(file_name)[0]
		print(file_name)

		with open(file_path, "r") as file:
			data = json.load(file)
			print(data)

		if "tempo" in data:
			if data["tempo"] is None:
				print(f"Tempo is None in file: {json_file}")

			try:
				audio_path = os.path.join(path_to_stems, get_wav_from_json(path_to_stems, file_name))
				print("audio path ", audio_path)
				print("loading audio bc first one seems to render empty")

				audio_file, sr = librosa.load(audio_path, sr = sr)
				print(audio_file.shape)

				tempo, _ = librosa.beat.beat_track(y=audio_file, sr=sr)
				tempo = float(tempo[0])

				print(tempo)
				print("data type of tempo: ", type(tempo))
				data["tempo"] = tempo

				with open(file_path, "w") as file:
					json.dump(data, file, indent=4)

			except FileNotFoundError as e:
				print(f"FIle not found: {file_path}")
			except Exception as e:
				print(f"Unexpected error: {e}")
		else:
			print(f"Tempo not found in file: {json_file}")




