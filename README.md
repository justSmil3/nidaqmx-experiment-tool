[#](#) Python Version used Python 3.14.3
# INFORMATION
this is a work in progress project, all content is subject to change 

# INSTALlATION

## Step 1: 
Clone this directory to a local folder

## Step 2: 
install [Python version 3.14.3](https://www.python.org/downloads/release/python-3143/). 
If you already have a local version installed, py --version, python --version or python3 --version should return the exact version installed. If the versions do not match, please consider installing or up-/downgrading to the matching version to ensure correct functionality. 

## Step 3: 
Create a virtual environmen: 
run <path to python executable> -m venv venv in the root directoy 
to acticate said environment do the following: 
### Windows
`venv/scripts/activate`
### Mac
`source venv/bin/activate`

to deactivate it run `deacticate`

## Step 3: 
Install needed dependencies
  - activate the virtual environment
  - run pip install -r requirements.txt
  
## Step 4: 
run the application with python -m streamlit run app/app.py from the root directore
