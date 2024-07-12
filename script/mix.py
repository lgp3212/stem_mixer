import os 
import glob
import random
import uuid
import soundfile as sf
import librosa

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