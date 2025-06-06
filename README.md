# MELJS
MELJS' UA&amp;P x Eskwelabs Hackathon Repository

## Instructions for running streamlit:
1. clone this repository on your local device
2. install the required libraries on your local python environment
3. move clean_data.csv into the data folder

## Instructions for editing:
1. Clone this Repository on your local device
2. Download the imports_main.csv data from the shared drive
3. Move the imports_main.csv into the raw_data folder

### If first time installation or there is an update in the requirements.txt or environment.yaml
1. Create or activate the virtual environment or conda environment
2. If using venv, run 'pip install -r requirements.txt'
3. If using conda, run 'conda env update -f environment.yaml'

### Notes on Final Data:
- only kept the top 45 countries from the raw imports data which is about 95.6% of the data
- used an approximate seadistance from the CERDI sea distance database
- for the tariff rates, it was simplified to the mfn_ad_valorem rate of the first hts8 code that matches the hs code that for all countries. 
- disregarded the month in the data. tariff rates were taken from the US 2024, however the wgi indicators were from 2023