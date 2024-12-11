# API_Access.py

A script to access the Riot API and create JSON files with information about ranked matches to feed our Mongo database
- champions/ = directory with 169 JSON files, one for each champion, containing lists with information related to a maximum of 40 matches played by OTPs with each champion
- roles/ = directory with 5 JSON files, one for each role, containing lists with information related to a maximum of 100 matches played by pro players on each role
- players/ = directory with N JSON files (in this case, 8), one for each casual player, containing lists with information related to a maximum of 60 matches played by each
- champs_dict.json = file with a champions dictionary with the format {name : id} (string : int)
- items_dict.json = file with an items dictionary with the format {id : name} (string : string)

## Requiriments to run the script

- install the required packages
- change the api_key variable in the main function since it expires every 24h hours
- switch the global variable isTest to True if you want to run the script in test mode, doing only 1 iteration for each function