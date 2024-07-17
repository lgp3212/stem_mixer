import argparse
import os
import metadata
import mix

def brid(file_path): # setting parameters for brid data
    """
    BRID DATASET PRE-PROCESSING

    Takes file path to BRID stems and assigns instrument variable based on file name

    Parameters:
    file_path (str) : path to stems

    Returns:
    tempo (float) : tempo of stem based on style
    instrument_name (str) : name of BRID instrument if exists
    key : null
    sound_class (str) : sound_class of BRID stem, "percussive"
    """

    key = None
    sound_class = "percussive"

    instrument_folders = {
            "-PD" : "pandeiro",
            "-TB": "tamborim",
            "-RR": "reco-reco",
            "-CX": "caixa",
            "-RP": "repique",
            "-CU": "cuica",
            "-AG": "agogo",
            "-SK": "shaker",
            "-TT": "tanta",
            "-SU": "surdo"}
    instrument_name = None
    for suffix in instrument_folders:
        if suffix in file_path:
            instrument_name = instrument_folders[suffix]


    folders = ["samba","marcha","partido alto","samba-enredo","other","capoeira"]

    style_dict = {
        "SA.wav" : "samba",
        "PA.wav": "partido alto",
        "CA.wav": "capoeira",
        "SE.wav": "samba-enredo",
        "MA.wav": "marcha",
        "OT.wav": "other"
    }

    style_to_tempo = {
        "samba" : 80.0,
        "partido alto" : 100.0,
        "samba-enredo" : 130.0,
        "marcha" : 120.0,
        "capoeira" : 65.0,
        "other" : None
    }

    style = None

    for suffix in style_dict:
        if suffix in file_path:
            style = style_dict[suffix]

    if style is None:
        tempo = None

    else:
        tempo = style_to_tempo[style]

    return tempo, instrument_name, key, sound_class


def musdb(file_path): # setting parameters for musdb data
    """
    MUSDB DATASET PRE-PROCESSING

    Takes file path to MUSDB stems and assigns variables based on file name

    Note: to make use of this function, save MUSDB stems as "artist - track_title - stem_title.wav"
    where stem_title is "vocals", "drums", "bass", or "other"

    i.e. "Bobby Nobody - Stich Up - drums.wav"

    Parameters:
    file_path (str) : path to stems

    Returns:
    tempo : null
    instrument_name (str) : name of MUSDB instrument / type if exists
    key : null
    sound_class : sound class of stem if instrument_name exists and is "vocals", "drums", "bass", or "other"
    """

    key = None
    tempo = None
    instrument_name = None
    sound_class = None

    type_folders = ["vocals", "drums", "bass", "other"]

    for name in type_folders:
        if name in file_path:

            instrument_name = name

            if instrument_name == "vocals":
                sound_class = "vocals"
            elif instrument_name == "drums":
                sound_class = "percussive"
            elif instrument_name == "bass" or instrument_name == "other":
                sound_class = "harmonic"
            else:
                sound_class = None


    return tempo, instrument_name, key, sound_class

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="PreprocessingHelper",
            description="This script creates metadata for BRID and/or MUSDB"
            )

    # arguments. required --> data home, dataset (if using preprocessing)
    parser.add_argument("--data_home", required=True, help="pathway to where is data is stored")
    parser.add_argument("--dataset", required=True, help="supported datasets: BRID (enter 'brid') and MUSDB (enter 'musdb')")
    parser.add_argument("--track_files", help="txt file with track names")
    # need to develop this still

    parser.add_argument("--sr", required=False, default=44100, help="sample rate, default is 44100Hz")
    parser.add_argument("--duration", required=False, default=10.0, help="mixture duration, default is 10 seconds")
    parser.add_argument("--n_mixtures", required=False, default=5, help="number of mixtures created")
    parser.add_argument("--n_stems", required=False, default=3, help="number of stems pertaining to each mix")
    parser.add_argument("--n_harmonic", required=False, default=0, help="number of harmonic stems")
    parser.add_argument("--n_percussive", required=False, default=0, help="number of percussive stems")


    args = parser.parse_args()
    kwargs = vars(args)
    path_to_stems = os.path.join(args.data_home, "stems")

    if args.dataset == "brid":

        for root, dirs, files in os.walk(path_to_stems):
            for file in files:
                file_path = os.path.join(root, file)
                args.tempo, args.instrument_name, args.key, args.sound_class = brid(file_path)

                # extracting unique metadata for all brid .wav files
                if file_path.endswith(".wav") or file_path.endswith(".mp3"):
                    metadata.extraction(file_path, **kwargs)


    elif args.dataset == "musdb":

        for root, dirs, files in os.walk(path_to_stems):
            for file in files:
                file_path = os.path.join(root, file)
                args.tempo, args.instrument_name, args.key, args.sound_class = musdb(file_path)
                print("instrument name ",args.instrument_name)

                # extracting unique metadata for all musdb .wav files
                if file_path.endswith(".wav") or file_path.endswith(".mp3"):
                    metadata.extraction(file_path, **kwargs)


    else:
        print(f"{args.dataset} is not a supported dataset.")


    count = 0
    args.n_mixtures = 2

    while count < args.n_mixtures: # count can only increase if valid mixture is made, lots of checks in place

        invalid_mixture = False

        base_stem_name, base_tempo, base_instrument, tempo_bin, json_percussive, json_harmonic, n_harmonic, n_percussive = mix.select_base_track(args.data_home, args.n_stems, args.n_harmonic, args.n_percussive)

        selected_stems, base_tempo, invalid_mixture = mix.select_top_tracks(base_stem_name, base_tempo, base_instrument, tempo_bin, 
            json_percussive, json_harmonic, args.n_stems, n_harmonic, n_percussive)

        stretched_audios, invalid_mixture = mix.stretch(args.data_home, args.sr, selected_stems, base_tempo, invalid_mixture, args.n_stems) 
        final_audios, invalid_mixture = mix.shift(args.sr, stretched_audios, invalid_mixture)

        
        invalid_mixture = mix.generate(args.data_home, args.sr, args.duration, invalid_mixture, final_audios)
        # final function returns if it is a valid mixture or not. if not, it repeats again
        
        if not invalid_mixture:
            print("")
            print("this is a valid mix")
            print("")
            count += 1

        








