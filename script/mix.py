import os 
import glob
import random
import uuid
import soundfile as sf
import librosa
import json

def generate(data_home, sr, n_stems = 4):

	# this mixture chooses random stems, we want to generate with stems already selected
	# and prepared?

	mixture_folder = os.path.join(data_home, "mixtures")
	os.makedirs(mixture_folder, exist_ok = True)

	path_to_stems = os.path.join(data_home, "stems")

	audio_files = glob.glob(os.path.join(path_to_stems, "*.wav")) + glob.glob(os.path.join(path_to_stems, "*.mp3"))

	if len(audio_files) < n_stems:
		raise ValueError(f"Not enough files in the directory to choose {num_files} random files.")

	random_files = random.sample(audio_files, n_stems)

	stem_audios = []
	stem_audio_lengths = []

	for stem in random_files:

		stem_audio,sr = librosa.load(stem, sr=sr)
		stem_audio_len = len(stem_audio)

		stem_audios.append(stem_audio)
		stem_audio_lengths.append(stem_audio_len)

	min_length = min(stem_audio_lengths)
	min_pos = stem_audio_lengths.index(min_length)
	mixture_audio = stem_audios[min_pos]

	truncated_stems = []
	for audio in stem_audios:
		audio = audio[:min_length]
		truncated_stems.append(audio)
	# concern: if somehow an empty stem ends up here, everything will get cut to 0s
	# pre-mixture filtering / cleaning process needed where all empty stems get deleted

	mixture_id = str(uuid.uuid4())
	individual_output_folder = os.path.join(mixture_folder, mixture_id)
	os.makedirs(individual_output_folder, exist_ok=True)

	for k in range(0, len(truncated_stems)):
		sf.write(f"{individual_output_folder}/stem{k+1}.wav", truncated_stems[k], sr)
		# check: what if mp3? or other type?

		if(k != min_pos): # already accounted for
			mixture_audio = mixture_audio + truncated_stems[k]

	sf.write(f"{individual_output_folder}/mixture.wav", mixture_audio, sr)

def select_base_track(data_home):
	path_to_stems = os.path.join(data_home, "stems")

	json_files = glob.glob(os.path.join(path_to_stems, "*.json"))
	json_percussive = []
	json_harmonic= []

	for file in json_files:
		with open(file, "r") as f:
			data = json.load(f)
			if data.get("sound_class") == "percussive":
				json_percussive.append(file)
			elif data.get("sound_class") == "harmonic" or data.get("sound_class") == "vocals":
				json_harmonic.append(file)

	audio_files = glob.glob(os.path.join(path_to_stems, "*.wav")) + glob.glob(os.path.join(path_to_stems, "*.mp3"))

	random_json_file = random.sample(json_percussive, 1)[0]
	with open(random_json_file, "r") as f:
			data = json.load(f)
			base_tempo = data.get("tempo")
			tempo_bin = data.get("tempo bin")


	split_name = os.path.basename(random_json_file)
	base_stem_name, _ = os.path.splitext(split_name)

	print("stem: ", base_stem_name)
	print("tempo base: ", base_tempo)
	print("tempo bin: ", tempo_bin)

	return base_stem_name, base_tempo, tempo_bin, json_percussive, json_harmonic

def select_top_tracks(base_stem_name, base_tempo, tempo_bin, json_percussive, json_harmonic, n_stems):

	print("base stem name to begin ", base_stem_name)

	invalid_mixture = False

	# need to make sure no repetition
	# return list of wav files. do we need list of json files?

	tempo_bin_harmonic = {}
	tempo_bin_percussive = {}

	for file in json_percussive:
		with open(file, "r") as f:
			data = json.load(f)
			if data.get("tempo bin") == tempo_bin:
				# checking that it is not file already picked
				split_name = os.path.basename(file)
				new_stem_name, _ = os.path.splitext(split_name)
				if new_stem_name != base_stem_name:
					tempo_bin_percussive[new_stem_name] = data.get("tempo")

	for file in json_harmonic:
		with open(file, "r") as f:
			data = json.load(f)
			if data.get("tempo bin") == tempo_bin:
				split_name = os.path.basename(file)
				new_stem_name, _ = os.path.splitext(split_name)
				if new_stem_name != base_stem_name:
					tempo_bin_harmonic[new_stem_name] = data.get("tempo")

	# right now just going to pick a harmonic track but i am keeping them separate above for when i add hp ratio later

	# for ratio purposes
	n_harmonic = n_stems - 1
	n_percussive = 0

	# how to deal with index out of bound error?
	# might want to create a flag for whether its a valid mixture or not. 
	selected_stems = {}
	selected_stems[base_stem_name] = base_tempo

	try:
		tempo_bin_harmonic_keys = list(tempo_bin_harmonic.keys())
		harmonic_stems = random.sample(tempo_bin_harmonic_keys, n_harmonic)

		tempo_bin_percussive_keys = list(tempo_bin_percussive.keys())
		percussive_stems = random.sample(tempo_bin_percussive_keys, n_percussive)

		for stem in harmonic_stems:
			split_name = os.path.basename(stem)
			new_stem_name, _ = os.path.splitext(split_name)
			tempo = tempo_bin_harmonic[new_stem_name]
			selected_stems[new_stem_name] = tempo

		for stem in percussive_stems:
			split_name = os.path.basename(stem)
			new_stem_name, _ = os.path.splitext(split_name)
			tempo = tempo_bin_percussive[new_stem_name]
			selected_stems[new_stem_name] = tempo

	except ValueError as e:
		invalid_mixture = True

	return selected_stems, base_tempo, invalid_mixture

def stretch(data_home, sr, selected_stems, base_tempo, invalid_mixture, n_stems):

	path_to_stems = os.path.join(data_home, "stems")
	audio_files = glob.glob(os.path.join(path_to_stems, "*.wav")) + glob.glob(os.path.join(path_to_stems, "*.mp3"))
	stretched_audios = []
	selected_stems_keys = list(selected_stems.keys())

	if invalid_mixture == False:
		target_tempo = base_tempo
		path_to_stems = os.path.join(data_home, "stems")

		for i in range(1, n_stems):
			stem_to_stretch = selected_stems_keys[i]
			current_tempo = selected_stems[stem_to_stretch]

			for file in audio_files:
				if stem_to_stretch in file:
					wav_file = file

			audio, sr = librosa.load(wav_file, sr=sr)
			new_rate = float(target_tempo / current_tempo)
			stretched_audio = librosa.effects.time_stretch(audio, rate = new_rate)

			stretched_audios.append(stretched_audio)

	# adding orignal audio to list
	for file in audio_files:
		if selected_stems_keys[0] in file:
			wav_file = file
	audio, sr = librosa.load(wav_file, sr=sr)
	stretched_audios.append(audio)

	if len(stretched_audios) != n_stems:
		invalid_mixture = True

	return stretched_audios, invalid_mixture






			




















