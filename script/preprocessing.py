import argparse
import os

import metadata

def brid(file_path):
    """
    BRID DATASET PRE-PROCESSING

    Takes file path to BRID stem and assigns instrument variable based on file name

    Parameters:
        file_path (str) : path to stem

    Returns:
        tempo (float) : tempo of stem based on style
        instrument_name (str) : name of BRID instrument if exists
        key : null
        sound_class (str) : sound_class of BRID stem, "percussive"
    """

    key = None
    sound_class = "percussive"

    suffix_list = file_path.split("-")

    suffix_to_instr = {
            "PD" : "pandeiro",
            "TB": "tamborim",
            "RR": "reco-reco",
            "CX": "caixa",
            "RP": "repique",
            "CU": "cuica",
            "AG": "agogo",
            "SK": "shaker",
            "TT": "tanta",
            "SU": "surdo" 
            }

    instr_suffix = suffix_list[1][0:2]
    instrument_name = suffix_to_instr.get(instr_suffix, None)

    suffix_to_tempo = {
        "SA.wav" : 80.0,
        "PA.wav": 100.0,
        "CA.wav": 65.0,
        "SE.wav": 130.0,
        "MA.wav": 120.0
    }

    # from dataset documentation, brid stems adhere to the following structure: [GID#] MX-YY-ZZ.wav
    style_suffix = suffix_list[-1]
    tempo = suffix_to_tempo.get(style_suffix, None)

    return tempo, instrument_name, key, sound_class


def musdb(file_path):
    """
    MUSDB DATASET PRE-PROCESSING

    Takes file path to MUSDB stem and assigns variables based on file name

    Note: to make use of this function, save MUSDB stems as "artist - track_title - stem_title.wav"
    where stem_title is "vocals", "drums", "bass", or "other"

    i.e. "Bobby Nobody - Stich Up - drums.wav"

    Parameters:
        file_path (str) : path to stem

    Returns:
        tempo : null
        instrument_name (str) : name of MUSDB instrument / type if exists
        key : null
        sound_class : sound class of stem if instrument_name exists and is "vocals", "drums", "bass", or "other"
    """

    key = None
    tempo = None
    sound_class = None

    # removing .wav extension
    stem_name = file_path.split("-")[-1].strip()[0:-4]

    instrument_name = stem_name if stem_name != "other" else None

    if stem_name == "vocals":
        sound_class = "vocals"
    elif stem_name == "drums":
        sound_class = "percussive"
    elif stem_name == "bass" or stem_name == "other":
        sound_class = "harmonic"

    return tempo, instrument_name, key, sound_class

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="PreprocessingHelper",
            description="This script creates metadata for BRID and/or MUSDB"
            )

    # arguments. required --> data home, dataset (if using preprocessing)
    parser.add_argument("--data_home", required=True, help="pathway to where is data is stored")
    parser.add_argument("--dataset", required=True, choices=["brid","musdb"], help="supported datasets: BRID (enter 'brid') and MUSDB (enter 'musdb')")
    parser.add_argument("--track_files", help="txt file with track names")
    # need to develop this still

    args = parser.parse_args()
    kwargs = vars(args)

    preprocessing_functions = {
        "brid" : brid,
        "musdb" : musdb
    }

    for root, dirs, files in os.walk(args.data_home):
        for file in files:
            file_path = os.path.join(root, file)
            args.tempo, args.instrument_name, args.key, args.sound_class = preprocessing_functions[args.dataset](file_path)

            # extracting unique metadata for all brid .wav files
            if file_path.endswith(".wav") or file_path.endswith(".mp3"):
                metadata.extraction(file_path, **kwargs)
