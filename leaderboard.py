import tkinter as tk
import time
import threading
import json
import os

class LeaderboardApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Leaderboard")
        self.master.configure(bg='black')

        # Define a janela como fullscreen
        self.master.attributes('-fullscreen', True)

        # Vincula a tecla 'Esc' para sair do modo fullscreen
        self.master.bind("<Escape>", self.exit_fullscreen)

        # Título
        self.title_label = tk.Label(master, text="High Scores", font=("Press Start 2P", 32), fg='red', bg='black')
        self.title_label.pack(pady=10)

        # Cabeçalho do Leaderboard
        self.header_label = tk.Label(master, text="Rank        Name          Score", font=("Press Start 2P", 24), fg='white', bg='black')
        self.header_label.pack(pady=10)

        # Frame para o leaderboard
        self.leaderboard_frame = tk.Frame(master, bg='black')
        self.leaderboard_frame.pack(pady=20)

        # Lista para armazenar as labels
        self.labels = []

        # Iniciar a thread para atualizar o leaderboard
        self.update_thread = threading.Thread(target=self.update_leaderboard, daemon=True)
        self.update_thread.start()

    def exit_fullscreen(self, event=None):
        self.master.attributes('-fullscreen', False)

    def update_leaderboard(self):
        while True:
            # Limpar labels existentes
            for label in self.labels:
                label.destroy()
            self.labels.clear()

            # Ler dados do arquivo JSON
            try:
                leaderboard_data = self.carregar_dados_json('races.json')

                # Criar um dicionário para armazenar os dados mais recentes por nome
                latest_data = {}
                for entry in leaderboard_data:
                    latest_data[entry["name"]] = (entry["id"], entry["name"], entry["tempo_total"])  # Mantém apenas a última entrada do nome

                # Converte o dicionário de volta para uma lista, mantendo apenas os valores mais recentes
                leaderboard_list = list(latest_data.values())

                # Ordenar o leaderboard baseado no tempo
                leaderboard_list.sort(key=lambda x: x[2])  # Ordena pelo tempo (menor é melhor)

                # Verificar a última entrada baseada no maior ID
                last_entry = max(leaderboard_list, key=lambda x: x[0])  # A última entrada pelo maior ID
                last_id, last_name, last_time = last_entry

                # Verifica a posição da última entrada no ranking
                last_entry_rank = self.posicao(leaderboard_list, last_time)

                # Verificar se a última entrada está no top 10
                is_last_entry_in_top_10 = last_entry in leaderboard_list[:10]

                # Adicionar as entradas do top 10
                for index, (entry_id, name, time_ms) in enumerate(leaderboard_list[:10]):
                    rank_suffix = self.get_rank_suffix(index + 1)
                    formatted_time = self.format_time(time_ms)  # Converter milissegundos para minutos e segundos
                    label_text = self.format_leaderboard_entry(index + 1, rank_suffix, name, formatted_time)

                    # Se o nome e o tempo correspondem à última entrada, destacar no top 10 (caso esteja nele)
                    if name == last_name and time_ms == last_time:
                        label = tk.Label(self.leaderboard_frame, text=label_text,
                                         font=("Press Start 2P", 20), fg='yellow', bg='black')
                    else:
                        label = tk.Label(self.leaderboard_frame, text=label_text,
                                         font=("Press Start 2P", 20), fg='white', bg='black')
                    
                    label.pack(anchor='w')
                    self.labels.append(label)

                # Se a última entrada está fora do top 10, destacá-la em amarelo abaixo
                if not is_last_entry_in_top_10:
                    rank_suffix = self.get_rank_suffix(last_entry_rank)
                    formatted_time = self.format_time(last_time)
                    new_entry_text = self.format_leaderboard_entry(last_entry_rank, rank_suffix, last_name, formatted_time)
                    new_entry_label = tk.Label(self.leaderboard_frame, text=new_entry_text,
                                               font=("Press Start 2P", 20), fg='yellow', bg='black')
                    new_entry_label.pack(anchor='w')
                    self.labels.append(new_entry_label)

            except FileNotFoundError:
                print("Arquivo JSON não encontrado.")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")

            self.master.update_idletasks()  # Atualiza a geometria da janela
            time.sleep(5)  # Espera 5 segundos antes de atualizar novamente

    def carregar_dados_json(self, json_races='races.json'):
        if os.path.exists(json_races):
            with open(json_races, 'r', encoding='utf-8') as file:
                races_data = json.load(file)
                return races_data["races"]
        else:
            print("Arquivo JSON não encontrado.")
            return []

    def posicao(self, leaderboard_data, new_time):
        # Determina a posição do novo tempo em relação aos dados existentes
        position = 1  # Posição inicial
        for _, _, time_ms in leaderboard_data:
            if new_time >= time_ms:
                position += 1  # Aumenta a posição se o novo tempo é pior (maior)
        return position

    def get_rank_suffix(self, rank):
        if 10 <= rank % 100 <= 20:  # Exceções para 11th, 12th, 13th
            suffix = 'TH'
        else:
            suffix = {1: 'ST', 2: 'ND', 3: 'RD'}.get(rank % 10, 'TH')
        return suffix

    def format_leaderboard_entry(self, rank, suffix, name, time_str):
        # Formata a string com traços entre os elementos
        return f"{rank}{suffix:<3}------   {name:<16}   -----    {time_str}"

    def format_time(self, time_ms):
        # Converte milissegundos para minutos, segundos e milissegundos
        total_seconds = time_ms / 1000
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = time_ms % 1000  # Obtém os milissegundos inteiros
        return f"{minutes}m {seconds}s {milliseconds:03d}ms"  # Retorna o formato "Xm Ys Zms" com 3 casas para milissegundos


if __name__ == '__main__':
    root = tk.Tk()
    app = LeaderboardApp(root)

    root.mainloop()
