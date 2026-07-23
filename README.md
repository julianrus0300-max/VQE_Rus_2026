## Fresh Set-up Installation Instructions (Run in order in terminal)
1. python3.11 -m venv .venv
    - set up virtual environment
    - call the specific python version if your imports require certain versions. The version may need to be downloaded globally. If you have an issue contact a superuser (Tom S.) for help.
2. source .venv/bin/activate
    - activate virtual environment
3. pip install -r requirements.txt

## Useful Commands
python login.py - login to your Quantinuum account
deactivate - close environment
source .venv/bin/activate - manually get into environment
pip list - check the modules installed
If you ever need to install any new import, replace inquanto-nexus and do: /home/rusj1/vsCode/InquantoEnv/.venv/bin/python -m pip install inquanto-nexus --index-url=https://dl.cloudsmith.io/SkInhKAV92sMAuDe/quantinuum/customer/python/simple/

## API-KEYS 
Example of what an API-Key looks like: KGGAI-PWTFJ-GHDKE-POWWQ

## Getting Started
1. Select new terminal from the drop down
2. Confirm (.venv) is active. If not, run script in Useful Commands to manually enter env.
3. Run login to confirm token access for using inquanto
    -  You may need to provide your API key to run your first calc. You can find that in browser when logged into inquanto
4. Confirm your imports with pip list
    - If you don't see inquanto, qulacs, etc. then you'll need to pip install the requirements.txt file with command in dresh set-up
5. Create a new python file and run calculations.