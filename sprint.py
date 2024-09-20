import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
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
    url = f"http://4.228.216.201:8666/STH/v1/contextEntities/type/TrackVision/id/urn:ngsi-ld:TRV:027/attributes/lap?lastN={lastN}"

    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        lap_data = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
        return lap_data
    except requests.RequestException as e:
        print(f"Erro ao obter dados: {e}")
        return []

def obter_horario_da_volta(lastN):
    """Obtém os dados de horário de uma volta"""
    url = f"http://4.228.216.201:8666/STH/v1/contextEntities/type/TrackVision/id/urn:ngsi-ld:TRV:027/attributes/time?lastN={lastN}"

    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        time_data = data['contextResponses'][0]['contextElement']['attributes'][0]['values']
        return time_data
    except requests.RequestException as e:
        print(f"Erro ao obter dados: {e}")
        return []

def plotar_grafico_horario(voltas_horario):
    """Gera gráfico de horário (horas:minutos:segundos:milissegundos)"""
    if not voltas_horario:
        print("Nenhum dado disponível para plotar.")
        return

    voltas = list(range(1, len(voltas_horario) + 1))
    tempos = [datetime.strptime(entry['recvTime'], "%Y-%m-%dT%H:%M:%S.%fZ") for entry in voltas_horario]

    plt.figure(figsize=(12, 6))
    plt.plot(voltas, tempos, marker='o', linestyle='-', color='r')

    plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S.%f'))

    plt.xticks(voltas)
    plt.title('Gráfico de Horário em Função das Voltas')
    plt.xlabel('Número de Voltas')
    plt.ylabel('Horário (Horas:Minutos:Segundos:Milissegundos)')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def converter_tempo(tempo_ms):
    """Converte milissegundos para minutos, segundos e milissegundos se necessário"""
    if tempo_ms >= 1000:
        minutos, resto = divmod(tempo_ms, 60000)
        segundos, milissegundos = divmod(resto, 1000)
        if minutos > 0:
            return f'{minutos}m {segundos}s {milissegundos}ms'
        else:
            return f'{segundos}s {milissegundos}ms'
    else:
        return f'{tempo_ms} ms'

def plotar_grafico_milisegundos(voltas_milisegundos):
    """Gera gráfico de tempo em milissegundos por volta e exibe o valor dos milissegundos em cada ponto"""
    if not voltas_milisegundos:
        print("Nenhum dado disponível para plotar.")
        return

    # Acessando os valores do JSON corretamente
    voltas = [entry['attrValue'][0] for entry in voltas_milisegundos]
    tempos = [entry['attrValue'][1] for entry in voltas_milisegundos]
    media_ = sum(tempos) / len(tempos)  # Calculando a média dos tempos

    # Criando o gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(voltas, tempos, marker='o', linestyle='-', color='r', label="Tempo por volta")
    plt.axhline(y=media_, color='b', linestyle='--', label="Média")

    # Adicionando os valores dos tempos (convertidos) acima de cada ponto
    for i, tempo in enumerate(tempos):
        tempo_formatado = converter_tempo(tempo)  # Converte o tempo
        plt.text(voltas[i], tempo + 100, tempo_formatado, ha='center', va='bottom', fontsize=9)

    # Configurando o gráfico
    plt.xticks(voltas)
    plt.title('Gráfico de Tempo por Volta')
    plt.xlabel('Número de Voltas')
    plt.ylabel('Tempo (Milissegundos)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()



def selecionar():
    """Seleciona a opção que o usuário deseja realizar"""
    while True:
        try:
            opcao = int(input(f"{AZUL}Selecione a opção desejada{LIMPAR}:\n1 - Gerar gráfico de horário\n2 - Gerar gráfico de tempo em milissegundos\n3 - Sair\n----> "))
            if opcao in [1, 2, 3]:
                break
            else:
                print(f"{VERMELHO}Número não se encaixa na quantidade de opções.{LIMPAR}")
                sleep(1.5)
                limpar_tela()
        except ValueError:
            print(f"{VERMELHO}Valor inválido digitado. Por favor, insira novamente.{LIMPAR}")
            sleep(1.5)
            limpar_tela()

    lastN = quantidade_de_dados()

    if opcao == 1:
        horario_voltas = obter_horario_da_volta(lastN)
        plotar_grafico_horario(horario_voltas)
    elif opcao == 2:
        tempo_voltas = obter_numero_voltas(lastN)
        plotar_grafico_milisegundos(tempo_voltas)
    elif opcao == 3:
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
