import requests
import json
import re
import time
from tenacity import retry, stop_after_attempt, wait_fixed
import os

MAX = 60
isTest = False # True = funções executarão no modo teste (apenas 1 iteração); False = funções executação completamente

def get_wait_time(header): # calcula o tempo de espera entre as chamadas de API (ChatGPT generated btw)
  # Extract rate limit information from header
    app_rate_limit = header.get('X-App-Rate-Limit', '').split(',')
    app_rate_limit_count = header.get('X-App-Rate-Limit-Count', '').split(',')

    method_rate_limit = header.get('X-Method-Rate-Limit', '').split(':')
    method_rate_limit_count = header.get('X-Method-Rate-Limit-Count', '').split(':')

  # Parse the first app rate limit (20:1)
    app_limit_1, app_window_1 = map(int, app_rate_limit[0].split(':'))
    app_count_1, _ = map(int, app_rate_limit_count[0].split(':'))

  # Parse the second app rate limit (100:120)
    app_limit_2, app_window_2 = map(int, app_rate_limit[1].split(':'))
    app_count_2, _ = map(int, app_rate_limit_count[1].split(':'))

  # Parse method-specific rate limits
    method_limit = int(method_rate_limit[0]) if len(method_rate_limit) == 2 else 0
    method_window = int(method_rate_limit[1]) if len(method_rate_limit) == 2 else 1 # Default to 1 second window
    method_count = int(method_rate_limit_count[0]) if len(method_rate_limit_count) == 2 else 0

  # Calculate remaining requests for the app rate limits
    app_remaining_1 = app_limit_1 - app_count_1
    app_remaining_2 = app_limit_2 - app_count_2

  # Calculate remaining requests for the method rate limit
    method_remaining = method_limit - method_count

  # Calculate wait times if the limit has been hit
    app_wait_time_1 = 0
    app_wait_time_2 = 0
    method_wait_time = 0

  # If the first app limit (20:1) is hit, calculate how long to wait
    if app_remaining_1 <= 0:
        app_wait_time_1 = app_window_1 # Wait for the entire window to reset

  # If the second app limit (100:120) is hit, calculate how long to wait
    if app_remaining_2 <= 0:
        app_wait_time_2 = app_window_2 # Wait for the entire window to reset

  # If the method limit is hit, calculate how long to wait
    if method_remaining <= 0:
        method_wait_time = method_window # Wait for the entire method window to reset

  # Return the maximum of all wait times to ensure we don't exceed any rate limit
    return max(app_wait_time_1, app_wait_time_2, method_wait_time)

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2)) # tenta a requisição em até 5x em caso de falha, com um intervalo de 2s entre cada tentativa
def make_request(url): # faz requisições HTTP
    resp = requests.get(url) # faz a requisição
    return resp

def build_json(dictionary, file_name): # transforma um dicionário num JSON
    print("\nbuild_json() started")
    start_time = time.time()
    with open(file=f"{file_name}.json", mode="w", encoding="utf-8") as f:
        json.dump(obj=dictionary, fp=f, ensure_ascii=False, indent=4)
    print(f"Arquivo {file_name}.json salvo com sucesso!")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("build_json() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} segundos")

def build_champion_dict(): # cria o dicionário dos campeões {nome : id} (string : int) com base na API do DataDragon
    print("\nbuild_champion_dict() started")
    start_time = time.time()
    champs_dict = {}
    version = "14.23"
    language = "en_US"
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}.1/data/{language}/champion.json"
    resp = make_request(url)
    data = {}
    if resp.status_code == 200: # se o request foi um sucesso
        data = resp.json()
        data = data["data"]
    else:
        print(f"Erro! Status {resp.status_code}")
    for i in data.items():
        champs_dict[i[1]["id"]] = int(i[1]["key"])
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("build_champion_dict() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} segundos")
    return champs_dict

def build_items_dict(): # cria o dicionário dos itens {id : nome} (string : string) com base na API do DataDragon
    print("\nbuild_items_dict() started")
    start_time = time.time()
    items_dict = {}
    version = "14.23"
    language = "en_US"
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}.1/data/{language}/item.json"
    resp = make_request(url)
    data = {}
    if resp.status_code == 200: # se o request foi um sucesso
        data = resp.json()
        data = data["data"]
    else:
        print(f"Erro! Status {resp.status_code}")
    for item_id, item_info in data.items():
        items_dict[item_id] = item_info["name"]
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("build_items_dict() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} segundos")
    return items_dict

def build_img_folder(items_dict, champs_dict): # cria uma pasta com as imagens dos campeões e itens
    print("\nbuild_img_folder() started")
    start_time = time.time()
    version = "14.23"
    os.makedirs("img", exist_ok=True)
    os.makedirs("img/item", exist_ok=True)
    for item_id, item_name in items_dict.items():
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}.1/img/item/{item_id}.png"
        resp = make_request(url)
        if resp.status_code == 200:
            with open(f"img/item/{item_id}.png", "wb") as f:
                f.write(resp.content)
        else:
            print(f"Erro! Status {resp.status_code}")
    print("Diretório 'img/item' criado e populado")
    os.makedirs("img/champion", exist_ok=True)
    for champ_id, champ_name in champs_dict.items():
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}.1/img/champion/{champ_id}.png"
        resp = make_request(url)
        if resp.status_code == 200:
            with open(f"img/champion/{champ_id}.png", "wb") as f:
                f.write(resp.content)
        else:
            print(f"Erro! Status {resp.status_code}")
    print("Diretório 'img/champion' criado e populado")
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print("build_img_folder() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} minutos")

def build_reversed_champs_dict(champ_dict): # inverte o dicionário dos campeões {id : nome}
    reversed_dict = {v : k for k, v in champ_dict.items()}
    return reversed_dict

def build_otps_dict(txt): # cria o dicionário de OTPs
    print("\nbuild_otps_dict() started")
    start_time = time.time()
    otps_dict = {}
  # formato {"MasterYi" : [{"gameName" : "Sinerias", "tagLine" : "EUW", "puuid" : 1889, "match_list" : []},
  # {"gameName" : "Indra", "tagLine" : "Wuju", "puuid" : 2000, "match_list" : []}]}
    with open(file=txt, mode="r", encoding="utf8") as f:
        while True:
            nome_champ = f.readline().strip() # nome do campeão (sem \n)
            otp = f.readline().strip() # dados do mono (sem \n)
            temp_list = re.split("[#-]", otp) # separada nome, id e server numa lista
            otp1 = {"gameName" : temp_list[0], "tagLine" : temp_list[1], "server" : temp_list[2], "puuid" : -1, "match_list" : []} # cria o dicionário do mono
            otp = f.readline().strip()
            temp_list = re.split("[#-]", otp)
            otp2 = {"gameName": temp_list[0], "tagLine": temp_list[1], "server": temp_list[2], "puuid" : -1, "match_list" : []}
            otps_dict[nome_champ] = [otp1, otp2] # cria o par nome do campeão e lista de monos no dicionário
            linha = f.readline() # lê a próxima linha
            if not linha: # se for string vazia (EOF)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print("build_otps_dict() finished")
                print(f"Tempo decorrido: {elapsed_time:.2f} segundos")
                return otps_dict # retorna o dicionário construído
          # se não for string vazia (EOF), é só a linha em branco entre os campeões e continua a iteração

def build_pros_dict(txt): # cria o dicionário de pro players
    print("\nbuild_pros_dict() started")
    start_time = time.time()
    pros_dict = {}
    with open(file=txt, mode="r", encoding="utf8") as f:
        while True:
            role = f.readline().strip() # nome da role (sem \n)
            pro = f.readline().strip() # dados do pro (sem \n)
            temp_list = re.split(r"[#-]", pro) # separada nome, id e server numa lista
            pro1 = {"gameName" : temp_list[0], "tagLine" : temp_list[1], "server" : temp_list[2], "puuid" : -1, "match_list" : []} # cria o dicionário do pro
            pro = f.readline().strip() # dados do primeiro pro (sem \n)
            temp_list = re.split(r"[#-]", pro) # separada nome, id e server numa lista
            pro2 = {"gameName": temp_list[0], "tagLine": temp_list[1], "server": temp_list[2], "puuid": -1, "match_list" : []}
            pro = f.readline().strip()
            temp_list = re.split(r"[#-]", pro)
            pro3 = {"gameName": temp_list[0], "tagLine": temp_list[1], "server": temp_list[2], "puuid": -1, "match_list" : []}
            pro = f.readline().strip()
            temp_list = re.split(r"[#-]", pro)
            pro4 = {"gameName": temp_list[0], "tagLine": temp_list[1], "server": temp_list[2], "puuid": -1, "match_list" : []}
            pro = f.readline().strip()
            temp_list = re.split(r"[#-]", pro)
            pro5 = {"gameName": temp_list[0], "tagLine": temp_list[1], "server": temp_list[2], "puuid": -1, "match_list" : []}
            pros_dict[role] = [pro1, pro2, pro3, pro4, pro5] # cria o par role e lista de pros no dicionário
            linha = f.readline() # lê a próxima linha
            if not linha: # se for string vazia (EOF)
                end_time = time.time()
                elapsed_time = (end_time - start_time) / 60
                print("build_pros_dict() finished")
                print(f"Tempo decorrido: {elapsed_time:.2f} minutos")
                return pros_dict # retorna o dicionário construído
          # se não for string vazia (EOF), é só a linha em branco entre os campeões e continua a iteração

def get_players_info(txt, keys_list, api_key): # função grande e feia que pega uma lista de Riot IDs e cria JSONs de partidas para cada player
    print("\nget_players_info() started")
    start_time = time.time()
    players_list = []
    global MAX
    with open(file=txt, mode="r", encoding="utf8") as f:
        numLinhas = len(f.readlines()) # conta quantas linhas tem o arquivo
        f.seek(0) # move o cabeçote de leitura de volta pro início
        for i in range(0, numLinhas):
            player = f.readline().strip() # dados do player (sem \n)
            temp_list = re.split(r"[#-]", player) # separada nome, id e server numa lista
            player = {"gameName": temp_list[0], "tagLine": temp_list[1], "server": temp_list[2], "puuid": -1, "match_list": []} # cria o dicionário do player
            url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{player["gameName"]}/{player["tagLine"]}?api_key={api_key}" # forma o URL da API
            resp = make_request(url) # faz o request dos puuids na API
            if resp.status_code == 200: # se o request foi um sucesso
                player_info = resp.json()
                player["puuid"] = player_info["puuid"] # escreve o puuid obtido no dicionário do player
            else:
                print(f"Erro! ({player["gameName"]}#{player["tagLine"]}) Status {resp.status_code}")
            time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
            players_list.append(player)
        for player in players_list: # itera sobre a lista de players
            server = ""
            if player["server"] in ["NA", "BR", "LAN", "LAS"]:
                server = "americas"
            elif player["server"] in ["KR", "JP"]:
                server = "asia"
            elif player["server"] in ["EUNE", "EUW", "TR", "RU"]:
                server = "europe"
            elif player["server"] in ["OCE", "PH", "SG", "TH", "TW", "VN"]:
                server = "sea"
            url = f"https://{server}.api.riotgames.com/lol/match/v5/matches/by-puuid/{player['puuid']}/ids?type=ranked&start=0&count={MAX}&api_key={api_key}"
            resp = make_request(url) # faz o request da lista de partidas na API
            ids = []
            if resp.status_code == 200: # se o request foi um sucesso
                ids.extend(resp.json())
                if not ids:
                    print(f"Lista de partidas vazia. Player {player['gameName']}#{player['tagLine']}")
                player["match_list"].extend(ids) # escreve o puuid obtido no dicionário do player
            else:
                print(f"Erro! ({player['gameName']}#{player['tagLine']}) Status {resp.status_code}")
            time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
        os.makedirs("players", exist_ok=True)
        for player in players_list:
            player_match_list = []
            for match_id in player["match_list"]: # itera sobre a lista de partidas (range(0,60))
                server = ""
                if player["server"] in ["NA", "BR", "LAN", "LAS"]:
                    server = "americas"
                elif player["server"] in ["KR", "JP"]:
                    server = "asia"
                elif player["server"] in ["EUNE", "EUW", "TR", "RU"]:
                    server = "europe"
                elif player["server"] in ["OCE", "PH", "SG", "TH", "TW", "VN"]:
                    server = "sea"
                url = f"https://{server}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
                resp = make_request(url) # faz o request na API
                if resp.status_code == 200: # se o request foi um sucesso
                    data_returned = resp.json()
                    participants = data_returned["metadata"]["participants"] # o player é identificado por um número de 0 a 9 dentro da partida
                    if player["puuid"] in participants:
                        index = participants.index(player["puuid"]) # obtém o índice do participante
                        match_data = {} # cria o dicionário que vai conter todos os dados relevantes da partida
                        for data in keys_list: # pega todos os dados relevantes da partida
                            match_data[data] = data_returned["info"]["participants"][index].get(data, None)
                        player_match_list.append(match_data) # adiciona essa partida à lista de partidas do jogador
                else:
                    print(f"Erro! player: ({player['gameName']}#{player['tagLine']} - match: {match_id}) Status {resp.status_code}")
                time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
            with open(file=f"players/{player['gameName']}-{player['tagLine']}.json", mode="w", encoding="utf-8") as json_file: # escreve o JSON do player
                json.dump(obj=player_match_list, fp=json_file, ensure_ascii=False, indent=4)
                print(f"{player['gameName']}-{player['tagLine']}.json criado com sucesso")
        end_time = time.time()
        elapsed_time = (end_time - start_time) / 60
        print("get_players_info() finished")
        print(f"Tempo decorrido: {elapsed_time:.2f} minutos")
        return players_list

def get_puuids(otps_dict, pros_dict, api_key): # pega puuids e atualiza os dicionários
    print("\nget_puuids() started")
    start_time = time.time()
    global isTest
    for campeao, otps in otps_dict.items(): # itera sobre o dicionário com as informações de todos os monos
        for player in otps: # itera sobre a lista de monos (range(0,2))
            url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{player["gameName"]}/{player["tagLine"]}?api_key={api_key}" # forma o URL da API
            resp = make_request(url) # faz o request na API
            if resp.status_code == 200: # se o request foi um sucesso
                player_info = resp.json()
                player["puuid"] = player_info["puuid"] # escreve o puuid obtido no dicionário de monos
            else:
                print(f"Erro! ({player["gameName"]}#{player["tagLine"]}) Status {resp.status_code}")
            time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
        if isTest:
            break
    for role, pros in pros_dict.items(): # itera sobre o dicionário com as informações de todos os pros
        for player in pros: # itera sobre a lista de pros (range(0,5))
            url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{player['gameName']}/{player['tagLine']}?api_key={api_key}" # forma o URL da API
            resp = make_request(url) # faz o request na API
            if resp.status_code == 200: # se o request foi um sucesso
                player_info = resp.json()
                player["puuid"] = player_info["puuid"] # escreve o puuid obtido no dicionário de pros
            else:
                print(f"Erro! ({player['gameName']}#{player['tagLine']}) Status {resp.status_code}")
            time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
        if isTest:
            break
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print("get_puuids() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} minutos")
    return

def get_match_id_list(otps_dict, pros_dict, api_key, which): # pega lista de ids de partidas e atualiza os dicionários
    print("\nget_match_id_list() started")
    start_time = time.time()
    global MAX
    global isTest
    if which == "otps" or which == "both":
        for campeao, lista_otps in otps_dict.items(): # itera sobre o dicionário com as informações de todos os monos
            for player in lista_otps: # itera sobre a lista de monos (range(0,2))
                server = ""
                if player["server"] in ["NA", "BR", "LAN", "LAS"]:
                    server = "americas"
                elif player["server"] in ["KR", "JP"]:
                    server = "asia"
                elif player["server"] in ["EUNE", "EUW", "TR", "RU"]:
                    server = "europe"
                elif player["server"] in ["OCE", "PH", "SG", "TH", "TW", "VN"]:
                    server = "sea"
                url = f"https://{server}.api.riotgames.com/lol/match/v5/matches/by-puuid/{player['puuid']}/ids?type=ranked&start=0&count={MAX}&api_key={api_key}"
                resp = make_request(url) # faz o request na API
                ids = []
                if resp.status_code == 200: # se o request foi um sucesso
                    ids.extend(resp.json())
                    if not ids:
                        print(f"Lista de partidas vazia. Player {player['gameName']}#{player['tagLine']}")
                    player["match_list"].extend(ids) # escreve o puuid obtido no dicionário de monos
                else:
                    print(f"Erro! ({player['gameName']}#{player['tagLine']}) Status {resp.status_code}")
                time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
            if isTest:
                break
    if which == "pros" or which == "both":
        for role, lista_pros in pros_dict.items(): # itera sobre o dicionário com as informações de todos os pros
            for player in lista_pros: # # itera sobre a lista de pros (range(0,5))
                server = ""
                if player["server"] in ["NA", "BR", "LAN", "LAS"]:
                    server = "americas"
                elif player["server"] in ["KR", "JP"]:
                    server = "asia"
                elif player["server"] in ["EUNE", "EUW", "TR", "RU"]:
                    server = "europe"
                elif player["server"] in ["OCE", "PH", "SG", "TH", "TW", "VN"]:
                    server = "sea"
                url = f"https://{server}.api.riotgames.com/lol/match/v5/matches/by-puuid/{player['puuid']}/ids?type=ranked&start=0&count={MAX}&api_key={api_key}"
                resp = make_request(url)
                ids = []
                if resp.status_code == 200: # se o request foi um sucesso
                    ids.extend(resp.json())
                    player["match_list"].extend(ids) # escreve o puuid obtido no dicionário de pros
                else:
                    print(f"Erro! ({player['gameName']}#{player['tagLine']}) Status {resp.status_code}")
                time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
            if isTest:
                break
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print("get_match_id_list() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} minutos")
    return

def get_match_info_keys_list(txt): # pega do txt a lista de chaves do JSON retornado pela API que queremos armazenar no BD
    print("\nget_match_info_keys_list() started")
    start_time = time.time()
    with open(file=txt, mode="r", encoding="utf8" ) as f:
        keys_list = [line.strip() for line in f.readlines()]
    end_time = time.time()
    elapsed_time = (end_time - start_time)
    print("get_match_info_keys_list() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} segundos")
    return keys_list

def get_match_info(otps_dict, pros_dict, keys_list, champs_dict, api_key, which): # filtra as infomações das partidas e cria os arquivos JSON (um para cada campeão/role)
    print("\nget_match_info() started")
    start_time = time.time()
    global MAX
    global isTest
    if which == "otps" or which == "both":
        os.makedirs("champions", exist_ok=True)
        for campeao, lista_otps in otps_dict.items(): # itera sobre o dicionário com as informações de todos os monos
            champ_match_list = [] # vai ter 20*2 appends
            for player in lista_otps: # itera sobre a lista de monos (range(0,2))
                count = 0 # contador de partidas válidas (jogadas com determinado campeão)
                for match_id in player["match_list"]: # itera sobre a lista de partidas (range(0,60)) para selecionar apenas 20
                    server = ""
                    if player["server"] in ["NA", "BR", "LAN", "LAS"]:
                        server = "americas"
                    elif player["server"] in ["KR", "JP"]:
                        server = "asia"
                    elif player["server"] in ["EUNE", "EUW", "TR", "RU"]:
                        server = "europe"
                    elif player["server"] in ["OCE", "PH", "SG", "TH", "TW", "VN"]:
                        server = "sea"
                    url = f"https://{server}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
                    resp = make_request(url) # faz o request na API
                    if resp.status_code == 200: # se o request foi um sucesso
                        data_returned = resp.json()
                        participants = data_returned["metadata"]["participants"] # o player é identificado por um número de 0 a 9 dentro da partida
                        if player["puuid"] in participants:
                            index = participants.index(player["puuid"]) # obtém o índice do participante
                            if data_returned["info"]["participants"][index]["championId"] == int(champs_dict[campeao]): # se essa partida for com o campeão desejado
                                match_data = {} # cria o dicionário que vai conter todos os dados relevantes da partida
                                for data in keys_list: # pega todos os dados relevantes da partida
                                    match_data[data] = data_returned["info"]["participants"][index].get(data, None)
                                champ_match_list.append(match_data) # adiciona essa partida à lista de partidas do campeão
                                count += 1 # incrementa o contador de partidas válidas
                    else:
                        print(f"Erro! player: ({player['gameName']}#{player['tagLine']} - match: {match_id}) Status {resp.status_code}")
                    time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
                    if count == 20: # se já chegou no limite de 20 partidas válidas
                        print(f"20 partidas válidas encontradas para {player['gameName']}#{player['tagLine']} com o campeão {campeao}")
                        break # sai do laço e vai pro próximo jogador/campeão
                    if count < 20 and player["match_list"].index(match_id) == MAX-1:
                        print(f"Apenas {count} partidas válidas encontradas para {player['gameName']}#{player['tagLine']} com o campeão {campeao}")
            with open(file=f"champions/{campeao}.json", mode="w", encoding="utf-8") as json_file: # escreve o JSON do campeão
                json.dump(obj=champ_match_list, fp=json_file, ensure_ascii=False, indent=4)
                print(f"{campeao}.json criado com sucesso")
            if isTest:
                break
        print("Diretório 'champions' criado e populado")
    if which == "pros" or which == "both":
        os.makedirs("roles", exist_ok=True)
        for role, lista_pros in pros_dict.items(): # itera sobre o dicionário com as informações de todos os pros
            role_match_list = [] # vai ter 20*5 appends
            for player in lista_pros: # itera sobre a lista de pros (range(0,5))
                count = 0 # contador de partidas válidas (jogadas em determinada role)
                for match_id in player["match_list"]: # itera sobre a lista de partidas (range(0,60)) para selecionar apenas 20
                    server = ""
                    if player["server"] in ["NA", "BR", "LAN", "LAS"]:
                        server = "americas"
                    elif player["server"] in ["KR", "JP"]:
                        server = "asia"
                    elif player["server"] in ["EUNE", "EUW", "TR", "RU"]:
                        server = "europe"
                    elif player["server"] in ["OCE", "PH", "SG", "TH", "TW", "VN"]:
                        server = "sea"
                    url = f"https://{server}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
                    resp = make_request(url) # faz o request na API
                    if resp.status_code == 200: # se o request foi um sucesso
                        data_returned = resp.json()
                        participants = data_returned["metadata"]["participants"] # o player é identificado por um número de 0 a 9 dentro da partida
                        if player["puuid"] in participants:
                            index = participants.index(player["puuid"]) # obtém o índice do participante
                            if data_returned["info"]["participants"][index]["individualPosition"] == role: # se essa partida for na role desejada
                                match_data = {} # cria o dicionário que vai conter todos os dados relevantes da partida
                                for data in keys_list: # pega todos os dados relevantes da partida
                                    match_data[data] = data_returned["info"]["participants"][index].get(data, None)
                                role_match_list.append(match_data) # adiciona essa partida à lista de partidas do campeão
                                count += 1 # incrementa o contador de partidas válidas
                    else:
                        print(f"Erro! player: ({player['gameName']}#{player['tagLine']} - match: {match_id}) Status {resp.status_code}")
                    time.sleep(get_wait_time(resp.headers)) # sleep dinâmico entre cada requisição para não ultrapassar o limite
                    if count == 20: # se já chegou no limite de 20 partidas válidas
                        print(f"20 partidas válidas encontradas para {player['gameName']}#{player['tagLine']} na role {role}")
                        break # sai do laço e vai pro próximo jogador/role
                    if count < 20 and player["match_list"].index(match_id) == MAX-1:
                        print(f"Apenas {count} partidas válidas encontradas para {player['gameName']}#{player['tagLine']} na role {role}")
            with open(file=f"roles/{role}.json", mode="w", encoding="utf-8") as json_file: # escreve o JSON da role
                json.dump(obj=role_match_list, fp=json_file, ensure_ascii=False, indent=4)
                print(f"{role}.json criado com sucesso")
            if isTest:
                break
        print("Diretório 'roles' criado e populado")
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print("get_match_info() finished")
    print(f"Tempo decorrido: {elapsed_time:.2f} minutos")
    return

def main():

    api_key = "RGAPI-f52b0bf9-f3e7-4058-af40-b5eed5a53784" # expira a cada 24h

    champs_dict = build_champion_dict()
    build_json(champs_dict, "champs_dict")
    items_dict = build_items_dict()
    build_json(items_dict, "items_dict")
    build_img_folder(items_dict, champs_dict)

    otps_dict = build_otps_dict("otps.txt")
    pros_dict = build_pros_dict("pros.txt")
    match_info_keys_list = get_match_info_keys_list("matchDataInfoList.txt")

    get_puuids(otps_dict, pros_dict, api_key)
    get_match_id_list(otps_dict, pros_dict, api_key, "both")
    get_match_info(otps_dict, pros_dict, match_info_keys_list, champs_dict, api_key, "both")

    get_players_info("players.txt", match_info_keys_list, api_key)

if __name__ == "__main__":
    main()