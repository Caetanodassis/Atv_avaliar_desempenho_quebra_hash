import hashlib
import time
import csv
import sys
from concurrent.futures import ProcessPoolExecutor

# Hash fornecido por você
HASH_ALVO = "ca6ae33116b93e57b87810a27296fc36"
TOTAL_COMBINACOES = 1_000_000_000 # 000.000.000 a 999.999.999

def verificar_intervalo(inicio, fim, hash_objetivo, thread_id):
    """Função de busca para cada thread."""
    for i in range(inicio, fim):
        candidato = f"{i:09d}".encode()
        if hashlib.md5(candidato).hexdigest() == hash_objetivo:
            return i
        
        # Mostra progresso apenas na thread 0 a cada 1 milhão de tentativas
        if thread_id == 0 and i % 1_000_000 == 0:
            percent = ((i - inicio) / (fim - inicio)) * 100
            sys.stdout.write(f"\rProgresso da Thread 0: {percent:.2f}%")
            sys.stdout.flush()
    return None

def executar_experimento():
    threads_lista = [1, 2, 4, 8, 12]
    resultados = []
    tempo_serial = 0

    print(f"Buscando senha para hash: {HASH_ALVO}\n")

    for n in threads_lista:
        print(f"--- Iniciando com {n} thread(s) ---")
        inicio_teste = time.time()
        
        chunk = TOTAL_COMBINACOES // n
        senha_encontrada = None
        
        with ProcessPoolExecutor(max_workers=n) as executor:
            futures = [executor.submit(verificar_intervalo, i*chunk, (i+1)*chunk if i != n-1 else TOTAL_COMBINACOES, HASH_ALVO, i) for i in range(n)]
            
            for f in futures:
                res = f.result()
                if res is not None:
                    senha_encontrada = f"{res:09d}"

        fim_teste = time.time()
        duracao = fim_teste - inicio_teste
        
        if n == 1: tempo_serial = duracao
        speedup = tempo_serial / duracao
        eficiencia = (speedup / n) * 100
        
        resultados.append([n, round(duracao, 2), round(speedup, 2), f"{eficiencia:.2f}%"])
        print(f"\nSenha encontrada: {senha_encontrada} | Tempo: {duracao:.2f}s")
        print(f"Speedup: {speedup:.2f}x | Eficiência: {eficiencia:.2f}%\n")

    # Gerar CSV para Excel
    with open('resultados_performance.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Threads', 'Tempo(s)', 'Speedup', 'Eficiencia(%)'])
        writer.writerows(resultados)
    
    print("Arquivo 'resultados_performance.csv' criado com sucesso.")

if __name__ == "__main__":
    executar_experimento()