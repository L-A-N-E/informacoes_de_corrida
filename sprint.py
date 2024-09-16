import requests
import matplotlib.pyplot as plt
from os import system, name
from time import sleep

# Definindo variáveis de cores e formatação de texto
LIMPAR = "\033[m"
VERMELHO = "\033[31m"
VERDE = "\033[32m"
AZUL = "\033[34m"
UNDERLINE = "\033[4m"
NEGRITO = "\033[1m"

def limpar_tela():
    """Limpa o terminal, seja no Windows ou Unix"""
    system('cls' if name == 'nt' else 'clear')

def sair():
    """Limpa o terminal, exibe mensagem e encerra o programa"""
    limpar_tela()
    print(f"{VERDE}Sistema finalizado. Tenha um bom dia!{LIMPAR}")
    return  

def obter_numero_voltas(lastN):
    """Obtém os dados diretamente da API usando uma requisição GET"""
    url = f"http://4.228.216.201:8666/STH/v1/contextEntities/type/Lamp/id/urn:ngsi-ld:Lamp:001/attributes/luminosity?lastN={lastN}"

    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Levanta um erro para status 4xx/5xx
        data = response.json()
        luminosity_data = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
        return luminosity_data
    except requests.RequestException as e:
        print(f"Erro ao obter dados: {e}")
        return []

def plotar_grafico(numero_voltas):
    """Gera gráfico de voltas em relação ao tempo"""
    if not numero_voltas:
        print("Nenhum dado disponível para plotar.")
        return

    voltas = [entry['attrValue'] for entry in numero_voltas]
    tempos = [entry['recvTime'] for entry in numero_voltas]

    media_ = sum(voltas) / len(voltas)

    plt.figure(figsize=(12, 6))
    plt.plot(tempos, voltas, marker='o', linestyle='-', color='r')
    plt.axhline(media_, color='b', linestyle='--', label=f'Média de Voltas: {media_:.2f}')
    plt.title('Gráfico de Voltas em Função do Tempo')
    plt.xlabel('Tempo')
    plt.ylabel('Voltas')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def selecionar():
    """Seleciona a opção que o usuário deseja realizar"""
    while True:
        try:
            opcao = int(input(f"{AZUL}Selecione a opção desejada{LIMPAR}:\n1 - Gerar gráfico de tempo\n2 - Sair\n----> "))
            if opcao in [1, 2]:
                break
            else:
                print(f"{VERMELHO}Número não se encaixa na quantidade de opções.{LIMPAR}")
                sleep(1.5)
                limpar_tela()
        except ValueError:
            print(f"{VERMELHO}Valor inválido digitado. Por favor, insira novamente.{LIMPAR}")
            sleep(1.5)
            limpar_tela()

    if opcao == 1:
        numero_voltas = obter_numero_voltas(quantidade_de_dados())
        plotar_grafico(numero_voltas)
    elif opcao == 2:
        sair()

def quantidade_de_dados():
    """Pergunta ao usuário a quantidade de dados para o gráfico e retorna o valor"""
    while True:
        try:
            lastN = int(input("Digite um valor para lastN (entre 1 e 100): "))
            if 1 <= lastN <= 100:
                return lastN
            else:
                print(f"{VERMELHO}O valor deve estar entre 1 e 100. Tente novamente.{LIMPAR}")
        except ValueError:
            print(f"{VERMELHO}Por favor, digite um número válido.{LIMPAR}")

def main():
    """Função principal que chama as outras funções"""
    selecionar()

# Executar o programa
if __name__ == "__main__":
    main()
