import os 
import glob
import random
import uuid
import soundfile as sf
import librosa
import json
import numpy as np

def generate(data_home, sr, duration, stretched_audios):

	for stem in (stretched_audios):
		print(len(stem))


	mixture_folder = os.path.join(data_home, "mixtures")
	os.makedirs(mixture_folder, exist_ok = True)

	stretched_audios_lengths = []
	for stem in stretched_audios:
		stretched_audios_lengths.append(len(stem))

	min_length = min(stretched_audios_lengths)
	min_pos = stretched_audios_lengths.index(min_length)


	total_length = min_length
	print("min_length ", min_length)


	center = total_length // 2
	start_sample = int(max(0, center - (duration * sr) // 2))
	end_sample = int(min(total_length, center + (duration * sr) // 2))


	truncated_stems = []
	for audio in stretched_audios:

		audio = audio[:min_length]
		audio = audio[start_sample:end_sample]
		truncated_stems.append(audio)

	mixture_audio = truncated_stems[0] # initialization

	for k in range(1, len(truncated_stems)):
		mixture_audio += truncated_stems[k]



	mixture_id = str(uuid.uuid4())
	individual_output_folder = os.path.join(mixture_folder, mixture_id)
	os.makedirs(individual_output_folder, exist_ok=True)


	for k in range(0, len(truncated_stems)):
		sf.write(f"{individual_output_folder}/stem{k+1}.wav", truncated_stems[k], sr)



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

def select_top_tracks(base_stem_name, base_tempo, tempo_bin, json_percussive, json_harmonic, n_stems, n_harmonic = 0, n_percussive = 0):

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
	if n_harmonic == 0 and n_percussive == 0:
		n_harmonic = n_stems // 2
		n_percussive = n_stems - n_harmonic

	print("number harmonic: ", n_harmonic)
	print("number percussive: ", n_percussive)

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
	audio_norm = librosa.util.normalize(audio)

	# normalizing audio 


	stretched_audios.append(audio_norm)

	if len(stretched_audios) != n_stems:
		invalid_mixture = True

	return stretched_audios, invalid_mixture

def shift(sr, stretched_audios, invalid_mixture): 

	first_downbeats = []
	final_audios = []

	for audio in stretched_audios:
		_, beat_times = librosa.beat.beat_track(y=audio, sr=sr)
		downbeat_times = librosa.frames_to_time(beat_times, sr=sr)
		first_downbeats.append(downbeat_times[0])

	earliest_beat = min(first_downbeats)

	earliest_beat_index = first_downbeats.index(earliest_beat)
	print(earliest_beat_index)

	immutable_audio = stretched_audios[earliest_beat_index]

	final_audios.append(immutable_audio)

	for i in range(0, len(stretched_audios)):
		if i != earliest_beat_index:
			shift_difference = np.abs(first_downbeats[i] - earliest_beat)
			silence_samples = int(shift_difference * sr)
			silence = np.zeros(silence_samples)

			final_audio = np.concatenate([silence, stretched_audios[i]])
			final_audios.append(final_audio)

			# checking for empty mixture
			if len(final_audio) == 0:
				invalid_mixture = True

	return final_audios, invalid_mixture
