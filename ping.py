import os
import time
from datetime import datetime, timedelta
import multiprocessing
import signal

# Defina os endereços que você deseja pingar
enderecos = {
    "dnsgoogle": "8.8.8.8",
    "roteador1": "192.168.109.1",
    "roteador2": "192.168.109.2"
}

# Intervalo de tempo entre os pings (em segundos)
intervalo = 1

# Diretório para salvar os arquivos de log
diretorio_logs = os.path.dirname(os.path.abspath(__file__))

# Limite de arquivos de log
limite_arquivos = 30

# Variável de controle para encerrar os processos
encerrar = multiprocessing.Event()

# Tempo total de execução (1 dia)
tempo_execucao = timedelta(minutes=1440)

def obter_nome_arquivo_log(nome):
    data_atual = datetime.now().strftime("%Y-%m-%d")
    nome_arquivo_log = f"ping_log_{nome}_{data_atual}.txt"
    return os.path.join(diretorio_logs, nome_arquivo_log)

def listar_arquivos_logs():
    arquivos = [f for f in os.listdir(diretorio_logs) if f.startswith("ping_log_") and f.endswith(".txt")]
    arquivos.sort()
    return arquivos

def remover_arquivo_mais_antigo():
    arquivos = listar_arquivos_logs()
    if len(arquivos) > limite_arquivos:
        arquivo_mais_antigo = os.path.join(diretorio_logs, arquivos[0])
        os.remove(arquivo_mais_antigo)

def ping(endereco):
    response = os.system(f"ping -n 1 {endereco} > nul")
    return response == 0

def escrever_log(mensagem, caminho_arquivo_log):
    with open(caminho_arquivo_log, "a") as arquivo_log:
        arquivo_log.write(f"{mensagem}\n")

def monitorar_ip(nome, endereco):
    caminho_arquivo_log = obter_nome_arquivo_log(nome)
    tempo_final = datetime.now() + tempo_execucao
    while datetime.now() < tempo_final and not encerrar.is_set():
        if ping(endereco):
            status = "online"
        else:
            status = "offline"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mensagem = f"[{timestamp}] {nome} ({endereco}) está {status}"
        escrever_log(mensagem, caminho_arquivo_log)
        
        time.sleep(intervalo)

def tratar_sinal(signal, frame):
    encerrar.set()

def main():
    data_atual = datetime.now().date()
    nova_data = datetime.now().date()
    if nova_data != data_atual:
        remover_arquivo_mais_antigo()
        data_atual = nova_data

    signal.signal(signal.SIGINT, tratar_sinal)
    
    processos = []

    for nome, endereco in enderecos.items():
        processo = multiprocessing.Process(target=monitorar_ip, args=(nome, endereco))
        processo.start()
        processos.append(processo)

    for processo in processos:
        processo.join()

    # Mensagem final
    print("Monitoramento finalizado.")

if __name__ == "__main__":
    main()
