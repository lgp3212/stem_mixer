import argparse
import os
import metadata
import mix

def brid(file_path):
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
        "capoeira" : 65.0
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


def musdb(file_path):
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

        else:
            instrument_name = None
            sound_class = None

    return tempo, instrument_name, key, sound_class

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="PreprocessingHelper",
            description="This script creates metadata for BRID and/or MUSDB"
            )
    parser.add_argument("--data_home", required=True, help="pathway to where is data is stored")
    parser.add_argument("--dataset", required=True, help="supported datasets: BRID (enter 'brid') and MUSDB (enter 'musdb')")
    parser.add_argument("--track_files", help="txt file with track names")
    parser.add_argument("--sr", required=False, default=44100, help="sample rate, default is 44100Hz")

    args = parser.parse_args()
    kwargs = vars(args)
    path_to_stems = os.path.join(args.data_home, "stems")

    if args.dataset == "brid":

        for root, dirs, files in os.walk(path_to_stems):
            for file in files:
                file_path = os.path.join(root, file)
                args.tempo, args.instrument_name, args.key, args.sound_class = brid(file_path)
                if file_path.endswith(".wav") or file_path.endswith(".mp3"):
                    metadata.extraction(file_path, **kwargs)
                    metadata.percussive_harmonic(file_path, args.sr)

    elif args.dataset == "musdb":

        for root, dirs, files in os.walk(path_to_stems):
            for file in files:
                file_path = os.path.join(root, file)
                args.tempo, args.instrument_name, args.key, args.sound_class = brid(file_path)
                if file_path.endswith(".wav") or file_path.endswith(".mp3"):
                    metadata.extraction(file_path, **kwargs)

    else:
        print(f"{args.dataset} is not a supported dataset.")


    mix.generate(args.data_home, args.sr, n_stems = 2)







