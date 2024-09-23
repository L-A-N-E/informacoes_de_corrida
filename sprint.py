# Importando as bibliotecas necessárias
import json
from scipy.interpolate import make_interp_spline
import numpy as np
from os import system, name
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import requests

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

def obter_dados_vm(url):
    """Tenta obter dados da VM. Retorna os dados ou None em caso de falha."""
    headers = {
        'fiware-service': 'smart',
        'fiware-servicepath': '/'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Erro ao obter dados da VM: {e}")
        return None

def carregar_dados_locais(json_interno):
    """Carrega os dados salvos localmente do JSON interno."""
    if os.path.exists(json_interno):
        with open(json_interno, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        print(f"Arquivo {json_interno} não encontrado.")
        return None

def salvar_dados_locais(json_interno, dados):
    """Salva os dados recebidos da VM no JSON interno."""
    with open(json_interno, 'w', encoding='utf-8') as file:
        json.dump(dados, file, indent=4)

def obter_dados(lastN, tipo_dado):
    """Obtém dados da VM ou JSON local"""
    if tipo_dado == 'voltas':
        url = f"http://74.249.83.253:8666/STH/v1/contextEntities/type/TrackVision/id/urn:ngsi-ld:TRV:027/attributes/lap?lastN={lastN}"
        json_interno = 'dados.json'
    else:
        url = f"http://74.249.83.253:8666/STH/v1/contextEntities/type/TrackVision/id/urn:ngsi-ld:TRV:027/attributes/lap?lastN={lastN}"
        json_interno = 'dados.json'

    dados_vm = obter_dados_vm(url)
    if dados_vm:
        print("Dados obtidos da VM com sucesso.")
        salvar_dados_locais(json_interno, dados_vm)
        return dados_vm
    else:
        print("Usando dados locais.")
        return carregar_dados_locais(json_interno)

def plotar_grafico_horario(voltas_horario):
    """Gera gráfico de horário (horas:minutos:segundos:milissegundos) com curva suavizada"""
    if not voltas_horario:
        print("Nenhum dado disponível para plotar.")
        return

    voltas = list(range(1, len(voltas_horario) + 1))
    tempos = [datetime.strptime(entry['recvTime'], "%Y-%m-%dT%H:%M:%S.%fZ") for entry in voltas_horario]

    # Convertendo os tempos em segundos (ou qualquer unidade contínua) para suavização
    tempos_segundos = [(tempo - tempos[0]).total_seconds() for tempo in tempos]

    # Gerando uma curva suavizada com Spline
    voltas_smooth = np.linspace(min(voltas), max(voltas), 300)  # Valores interpolados para suavização
    spline = make_interp_spline(voltas, tempos_segundos, k=3)  # Interpolação spline cúbica
    tempos_smooth = spline(voltas_smooth)

    # Criando o gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(voltas, tempos, marker='o', linestyle='-', color='r', label="Horário por volta")

    # Adicionando a linha azul suavizada
    tempos_smooth_datetime = [tempos[0] + timedelta(seconds=seg) for seg in tempos_smooth]  # Convertendo de volta para datetime
    plt.plot(voltas_smooth, tempos_smooth_datetime, color='b', linestyle='-', label="Curva de função média em relação ao tempo")

    # Adicionando os valores dos horários diretamente no gráfico
    for i, tempo in enumerate(tempos):
        tempo_formatado = tempo.strftime('%H:%M:%S.%f')[:-3]  # Formatando para horas:minutos:segundos:milissegundos
        plt.text(voltas[i], tempo + timedelta(seconds=0.1), tempo_formatado, ha='center', va='bottom', fontsize=9)  # Ajuste de posição

    # Configurações do gráfico
    plt.gca().yaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.xticks(voltas)
    plt.title('Gráfico de Horário em Função das Voltas com Curva Suavizada')
    plt.xlabel('Número de Voltas')
    plt.ylabel('Horário (Horas:Minutos:Segundos:Milissegundos)')
    plt.grid(True)
    plt.legend()
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

    voltas = [entry['attrValue'][0] for entry in voltas_milisegundos]
    tempos = [entry['attrValue'][1] for entry in voltas_milisegundos]
    media_ = sum(tempos) / len(tempos)  # Calculando a média dos tempos

    plt.figure(figsize=(12, 6))
    plt.plot(voltas, tempos, marker='o', linestyle='-', color='r', label="Tempo por volta")
    plt.axhline(y=media_, color='b', linestyle='--', label="Média")

    for i, tempo in enumerate(tempos):
        tempo_formatado = converter_tempo(tempo)
        plt.text(voltas[i], tempo + 100, tempo_formatado, ha='center', va='bottom', fontsize=9)

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

    if opcao == 1:
        lastN = quantidade_de_dados()
        horario_voltas = obter_dados(lastN, 'horarios')
        plotar_grafico_horario(horario_voltas['contextResponses'][0]['contextElement']['attributes'][0]['values'])
    elif opcao == 2:
        lastN = quantidade_de_dados()
        tempo_voltas = obter_dados(lastN, 'voltas')
        plotar_grafico_milisegundos(tempo_voltas['contextResponses'][0]['contextElement']['attributes'][0]['values'])
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
