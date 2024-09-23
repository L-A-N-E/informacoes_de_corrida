# Importando as bibliotecas necessárias
import json
import os
from time import sleep
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import requests
from scipy.interpolate import make_interp_spline

# Definindo variáveis de cores e formatação de texto
LIMPAR = "\033[m"
VERMELHO = "\033[31m"
VERDE = "\033[32m"
AZUL = "\033[34m"
UNDERLINE = "\033[4m"
NEGRITO = "\033[1m"

def limpar_tela():
    """Limpa o terminal, seja no Windows ou Unix"""
    os.system('cls' if os.name == 'nt' else 'clear')

def sair():
    """Limpa o terminal, exibe mensagem e encerra o programa"""
    limpar_tela()
    print(f"{VERDE}Sistema finalizado. Tenha um bom dia!{LIMPAR}")
    exit()

def tamanho_pista():
    """Usuário insere o tamanho da pista para o cálculo de média da velocidade"""
    while True:
        try:
            tamanho = float(input("Digite o tamanho da pista em metros: "))
            if tamanho > 0:
                break
            else:
                print(f"{VERMELHO}Valor inválido, por favor digite um positivo maior do que zero.{LIMPAR}")
                sleep(1.5)
                limpar_tela()
        except ValueError:
            print(f"{VERMELHO}Por favor digite um valor válido.{LIMPAR}")
    return tamanho

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
        print(f"{VERMELHO}Erro ao obter dados da VM: {e}{LIMPAR}")
        return None

def carregar_dados_locais(json_interno):
    """Carrega os dados salvos localmente do JSON interno."""
    if os.path.exists(json_interno):
        with open(json_interno, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        print(f"{VERMELHO}Arquivo {json_interno} não encontrado.{LIMPAR}")
        return None

def salvar_dados_locais(json_interno, dados):
    """Salva os dados recebidos da VM no JSON interno."""
    with open(json_interno, 'w', encoding='utf-8') as file:
        json.dump(dados, file, indent=4)

def obter_dados(lastN):
    """Obtém dados da VM ou JSON local"""
    url = f"http://74.249.83.253:8666/STH/v1/contextEntities/type/TrackVision/id/urn:ngsi-ld:TRV:027/attributes/lap?lastN={lastN}"
    json_interno = 'dados.json'

    dados_vm = obter_dados_vm(url)
    if dados_vm:
        print(f"{VERDE}Dados obtidos da VM com sucesso.{LIMPAR}")
        salvar_dados_locais(json_interno, dados_vm)
        return dados_vm
    else:
        print(f"{AZUL}Usando dados locais.{LIMPAR}")
        return carregar_dados_locais(json_interno)

def plotar_grafico_horario(voltas_horario):
    """Gera gráfico de horário (horas:minutos:segundos:milissegundos) com curva suavizada"""
    if not voltas_horario:
        print(f"{VERMELHO}Nenhum dado disponível para plotar.{LIMPAR}")
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

def mostrar_volta_mais_rapida(voltas_milisegundos):
    """Exibe a volta mais rápida em termos de tempo"""
    if not voltas_milisegundos:
        print(f"{VERMELHO}Nenhum dado disponível.{LIMPAR}")
        return
    volta_mais_rapida = min(voltas_milisegundos, key=lambda x: x['attrValue'][1])
    volta_numero = volta_mais_rapida['attrValue'][0]
    tempo_mais_rapido = converter_tempo(volta_mais_rapida['attrValue'][1])
    print(f"{NEGRITO}{UNDERLINE}{VERDE}A volta mais rápida foi a volta {volta_numero}, com tempo de {tempo_mais_rapido}.{LIMPAR}")

def mostrar_volta_mais_lenta(voltas_milisegundos):
    """Exibe a volta mais lenta em termos de tempo"""
    if not voltas_milisegundos:
        print(f"{VERMELHO}Nenhum dado disponível.{LIMPAR}")
        return
    volta_mais_lenta = max(voltas_milisegundos, key=lambda x: x['attrValue'][1])
    volta_numero = volta_mais_lenta['attrValue'][0]
    tempo_mais_lento = converter_tempo(volta_mais_lenta['attrValue'][1])
    print(f"{NEGRITO}{UNDERLINE}{VERDE}A volta mais lenta foi a volta {volta_numero}, com tempo de {tempo_mais_lento}.{LIMPAR}")

def mostrar_velocidade_media_mais_rapida(voltas_milisegundos, tamanho):
    """Exibe a maior velocidade média calculada"""
    if not voltas_milisegundos or tamanho <= 0:
        print(f"{VERMELHO}Nenhum dado ou pista inválida.{LIMPAR}")
        return
    velocidades = [(entry['attrValue'][0], tamanho / (entry['attrValue'][1] / 1000)) for entry in voltas_milisegundos]
    volta_mais_rapida = max(velocidades, key=lambda x: x[1])
    print(f"{NEGRITO}{UNDERLINE}{VERDE}A maior velocidade média foi na volta {volta_mais_rapida[0]} com {volta_mais_rapida[1]:.2f} m/s.{LIMPAR}")

def mostrar_velocidade_media_mais_baixa(voltas_milisegundos, tamanho):
    """Exibe a menor velocidade média calculada"""
    if not voltas_milisegundos or tamanho <= 0:
        print(f"{VERMELHO}Nenhum dado ou pista inválida.{LIMPAR}")
        return
    velocidades = [(entry['attrValue'][0], tamanho / (entry['attrValue'][1] / 1000)) for entry in voltas_milisegundos]
    volta_mais_lenta = min(velocidades, key=lambda x: x[1])
    print(f"{NEGRITO}{UNDERLINE}{VERDE}A menor velocidade média foi na volta {volta_mais_lenta[0]} com {volta_mais_lenta[1]:.2f} m/s.{LIMPAR}")

def mostrar_velocidade_especifica(voltas_milisegundos, tamanho, volta_especifica):
    """Mostra a velocidade e velocidade média de uma volta específica"""
    if not voltas_milisegundos or tamanho <= 0:
        print(f"{VERMELHO}Nenhum dado ou pista inválida.{LIMPAR}")
        return
    for entry in voltas_milisegundos:
        if entry['attrValue'][0] == volta_especifica:
            tempo = entry['attrValue'][1]
            velocidade = tamanho / (tempo / 1000)
            print(f"{NEGRITO}{UNDERLINE}{VERDE}A velocidade da volta {volta_especifica} foi de {velocidade:.2f} m/s com tempo de {converter_tempo(tempo)}.{LIMPAR}")
            return
    print(f"{VERMELHO}Volta {volta_especifica} não encontrada.{LIMPAR}")

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
        print(f"{VERMELHO}Nenhum dado disponível para plotar.{LIMPAR}")
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
    
def plotar_grafico_velocidade_media(voltas_milisegundos, tamanho_pista):
    """Gera gráfico da velocidade média por volta com base no comprimento da pista."""
    if not voltas_milisegundos:
        print(f"{VERMELHO}Nenhum dado disponível para plotar.{LIMPAR}")
        return

    voltas = [entry['attrValue'][0] for entry in voltas_milisegundos]
    tempos = [entry['attrValue'][1] for entry in voltas_milisegundos]
    
    # Calculando a velocidade média (distância/tempo)
    velocidades = [(tamanho_pista / (tempo / 1000)) for tempo in tempos]  # Convertendo tempo de ms para segundos
    plt.figure(figsize=(12, 6))
    plt.plot(voltas, velocidades, marker='o', linestyle='-', color='g', label="Velocidade por volta (m/s)")
    plt.axhline(y=np.mean(velocidades), color='b', linestyle='--', label="Média de Velocidade")

    for i, velocidade in enumerate(velocidades):
        plt.text(voltas[i], velocidade + 0.1, f'{velocidade:.2f} m/s', ha='center', va='bottom', fontsize=9)

    plt.xticks(voltas)
    plt.title(f'Gráfico de Velocidade Média (Distância = {tamanho_pista}m)')
    plt.xlabel('Número de Voltas')
    plt.ylabel('Velocidade (m/s)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def selecionar():
    """Seleciona a opção que o usuário deseja realizar"""
    while True:
        try:
            opcao = int(input(f"{AZUL}Selecione a opção desejada{LIMPAR}:\n"
                                "1 - Gerar gráfico de horário\n"
                                "2 - Gerar gráfico de tempo em milissegundos\n"
                                "3 - Gerar gráfico de média de velocidade\n"
                                "4 - Mostrar volta mais rápida\n"
                                "5 - Mostrar volta mais lenta\n"
                                "6 - Mostrar velocidade mais rápida\n"
                                "7 - Mostrar velocidade mais lenta\n"
                                "8 - Mostrar velocidade de uma volta específica\n"
                                "9 - Sair\n----> "))
            if opcao in range(1, 10):
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
        limpar_tela()
        horario_voltas = obter_dados(lastN)
        plotar_grafico_horario(horario_voltas['contextResponses'][0]['contextElement']['attributes'][0]['values'])
    elif opcao == 2:
        lastN = quantidade_de_dados()
        limpar_tela()
        tempo_voltas = obter_dados(lastN)
        plotar_grafico_milisegundos(tempo_voltas['contextResponses'][0]['contextElement']['attributes'][0]['values'])
    elif opcao == 3:
        lastN = quantidade_de_dados()
        pista = tamanho_pista()
        limpar_tela()
        tempo_voltas = obter_dados(lastN)
        plotar_grafico_velocidade_media(tempo_voltas['contextResponses'][0]['contextElement']['attributes'][0]['values'], pista)
    elif opcao == 4:
        voltas_milisegundos = obter_dados(quantidade_de_dados())['contextResponses'][0]['contextElement']['attributes'][0]['values']
        limpar_tela()
        mostrar_volta_mais_rapida(voltas_milisegundos)
    elif opcao == 5:
        voltas_milisegundos = obter_dados(quantidade_de_dados())['contextResponses'][0]['contextElement']['attributes'][0]['values']
        limpar_tela()
        mostrar_volta_mais_lenta(voltas_milisegundos)
    elif opcao == 6:
        voltas_milisegundos = obter_dados(quantidade_de_dados())['contextResponses'][0]['contextElement']['attributes'][0]['values']
        tamanho = tamanho_pista()
        limpar_tela()
        mostrar_velocidade_media_mais_rapida(voltas_milisegundos, tamanho)
    elif opcao == 7:
        voltas_milisegundos = obter_dados(quantidade_de_dados())['contextResponses'][0]['contextElement']['attributes'][0]['values']
        tamanho = tamanho_pista()
        limpar_tela()
        mostrar_velocidade_media_mais_baixa(voltas_milisegundos, tamanho)
    elif opcao == 8:
        while True:
            try:
                voltas_milisegundos = obter_dados(quantidade_de_dados())['contextResponses'][0]['contextElement']['attributes'][0]['values']
                tamanho = tamanho_pista()
                volta_especifica = int(input("Digite o número da volta específica: "))
                limpar_tela()
                mostrar_velocidade_especifica(voltas_milisegundos, tamanho, volta_especifica)
                break
            except ValueError:
                print(f"{VERMELHO}Por favor, insira um número válido.{LIMPAR}")
    elif opcao == 9:
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
    while True:
        try:
            selecionar()
        except Exception as e:
            print(f"{VERMELHO}Ocorreu um erro: {str(e)}{LIMPAR}")
            sleep(1.5)
            limpar_tela()

# Executar o programa
if __name__ == "__main__":
    main()
