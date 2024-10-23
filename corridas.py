import requests
import json
import os
import time

def obter_dados() -> dict | None:
    """Obtém dados da VM ou JSON local"""
    url = f"http://20.206.249.122:8666/STH/v1/contextEntities/type/TrackVision/id/urn:ngsi-ld:TRV:027/attributes/lap?lastN=10"
    json_interno = 'dados.json'

    dados_vm = obter_dados_vm(url)
    if dados_vm:
        print("Dados obtidos da VM com sucesso.")
        salvar_dados_locais(json_interno, dados_vm)
        return dados_vm
    else:
        print('Um erro inesperado aconteceu')
        exit()
    
def obter_dados_vm(url: str) -> dict | None:
    """Tenta obter dados da VM. Retorna os dados ou None em caso de falha."""
    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }
    try:
        # Adiciona um tempo limite para a requisição
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.Timeout:
        print("Erro: Tempo de conexão esgotado ao tentar obter dados da VM")
    except requests.RequestException as e:
        print(f"Erro ao obter dados da VM: {e}")
    return None

def salvar_dados_locais(json_interno: str, dados: dict) -> None:
    """Salva os dados recebidos da VM no JSON interno."""
    with open(json_interno, 'w', encoding='utf-8') as file:
        json.dump(dados, file, indent=4)
        

def calcular_tempo_total(dados_voltas):
    """Função para somar o tempo total das voltas"""
    tempo_total = 0
    for volta in dados_voltas:
        tempo_total += volta["attrValue"][1]  # Soma os tempos (em milissegundos)
    return tempo_total


def gerar_novo_json(dados_vm, nome_usuario, json_races='races.json'):
    """Função para gerar o novo JSON com os dados da corrida, incluindo o nome do usuário"""
    # Carregar JSON existente, se houver
    if os.path.exists(json_races):
        with open(json_races, 'r', encoding='utf-8') as file:
            races_data = json.load(file)
    else:
        races_data = {"races": []}
    
    # Extrair voltas do JSON retornado pela VM
    voltas = dados_vm["contextResponses"][0]["contextElement"]["attributes"][0]["values"]
    
    # Calcular tempo total das voltas
    tempo_total = calcular_tempo_total(voltas)
    
    # Atribuir ID incremental
    if races_data["races"]:
        novo_id = races_data["races"][-1]["id"] + 1
    else:
        novo_id = 1
    
    # Adicionar nova corrida ao JSON com o nome do usuário
    nova_corrida = {
        "name": nome_usuario,
        "tempo_total": tempo_total,
        "id": novo_id
    }
    races_data["races"].append(nova_corrida)
    
    # Salvar o novo JSON
    with open(json_races, 'w', encoding='utf-8') as file:
        json.dump(races_data, file, indent=4)

    print(f"Corrida adicionada com sucesso! Nome: {nome_usuario}, ID: {novo_id}, Tempo total: {tempo_total}ms")

# Função de exemplo para simular a inserção do nome do usuário
def iniciar_corrida():
    nome_usuario = input("Digite o nome do usuário para esta corrida: ").capitalize()
    
    # Ler os dados diretamente do arquivo 'dados.json'
    with open('dados.json', 'r', encoding='utf-8') as file:
        dados_vm = json.load(file)
    
    gerar_novo_json(dados_vm, nome_usuario)

while True:
    menu = int(input('O código deverá ser compilado?\n1-Sim\n2-Não\n--->'))
    if menu == 1:
        obter_dados()
        time.sleep(1)
        iniciar_corrida()
    else:
        print('Finalizando sistema')
        exit()