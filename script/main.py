import argparse
import preprocessing as pre
import os
import metadata

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		prog="StemMixer",
		description="Generating mixtures"
	)
	parser.add_argument("--data_home", required=True, help="pathway to where is data is stored")
	# not sure if i want to do where data is stored or where stems are stored
	parser.add_argument("--output_folder", required=False, help="pathway to where mixtures will be stored. if not provided package will construct a folder called 'output' off of data_home")

	parser.add_argument("--tempo", default=None, required=False, help="add tempo if all stems pertain to same tempo. else: leave null and use dataset_specific pre-processing")
	parser.add_argument("--instrument_name", default=None, required=False, help="add instrument name if all stems pertain to same instrument. else: leave null and use dataset_specific pre-processing")
	parser.add_argument("--key", default=None, required=False, help="add key if all stems pertain to same key. else: leave null and use dataset_specific pre-processing")
	parser.add_argument("--sound_class", default=None, required=False, help="sound classes: percussive/harmonic/vocal. add sound class if all stems pertain to same sound class. else: leave null and use dataset_specific pre-processing")

	parser.add_argument("--duration", type=float, default=5.0, required=False, help="set mixture duration. default is 5 seconds")
	parser.add_argument("--sr", type=int, default=44100, required=False, help="set sample rate. default is 44100 Hz")

	args = parser.parse_args()

	# kind of view this process like inheritance, we start with nothing and structure slowly fills in

	path_to_stem_test = os.path.join(args.data_home, "stems/[0282] S3-PD2-02-PA.wav")

	args.tempo, args.instrument_name, args.key, args.sound_class = pre.brid(path_to_stem_test)

	path_to_stem_test = os.path.join(args.data_home, "stems/Enda Reilly - Cur An Long Ag Seol.wav")
	args.tempo, args.instrument_name, args.key, args.sound_class = pre.musdb(path_to_stem_test)

	metadata.extraction(path_to_stem_test, args.tempo, args.instrument_name, args.key, args.sound_class)

	# instructions: 
	# add data of one dataset, use pre-processing functions if applicable or do own pre-processing
	# with no pre-processing, all starting values will be None 
	# run metadata dictionary after each dataset addition, we want dictionaries to 
	# include as much dataset specific information as possible
	# LOOKING TO CONSOLIDATE THIS PROCESS, IT WORKS FOR NOW BUT I THINK IT COULD BE MORE EFFICIENT

	# once metadata structure is set, we fill in the rest and generate mixtures

