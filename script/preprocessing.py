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

    #if style in style_to_tempo:
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
    # reassign arg.parse args to these values?
            



