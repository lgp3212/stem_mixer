# stem_mixer
# example usage // without dataset-specific pre-processing
if you want to generate mixtures, you do the following

```bash
python script/main.py
--data_home=<path_to_folder>
```

to see other variables available, please run

`python script/main.py --help`

# example usage // dataset-specific pre-processing 
SUPPORTED DATASETS:
- BRID (Brazilian Rhythmic Instruments Dataset)
- MUSDB18* 

*note: if using MUSDB18, pre-pre-processing step required --> 
- must save each stem with "vocals", "drums", "bass", "other" in .wav filename 

if you want to generate mixtures using supported datasets, you do the following

```bash
python script/preprocessing.py
--data_home=<path_to_folder>
--dataset=<"brid" or "musdb">
```

to see other variables available, please run

`python script/preprocessing.py --help`

# Folder structure
We expect the following folder structure:

- data_home
    - stems
