import matplotlib.pyplot as plt
import numpy as np
import time
import math

# ------------------------------------------
# LOG BÁSICO
# ------------------------------------------
def log(msg):
    with open("execution.log", "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

# ------------------------------------------
# MÉTRICA: TIEMPO DE EJECUCIÓN
# ------------------------------------------
def measure_time(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed

# ------------------------------------------
# MÉTRICA: ENTROPÍA DE SHANNON
# ------------------------------------------
def compute_entropy(data: bytes):
    if not data:
        return 0.0

    freq = [0] * 256
    for b in data:
        freq[b] += 1

    entropy = 0
    n = len(data)

    for f in freq:
        if f > 0:
            p = f / n
            entropy -= p * math.log2(p)

    log(f"Entropía: {entropy:.4f} bits por byte")
    return entropy

# ------------------------------------------
# MÉTRICA: DISTANCIA DE AVALANCHA (bits distintos)
# ------------------------------------------
def avalanche_distance(c1: bytes, c2: bytes):
    dist = 0
    for b1, b2 in zip(c1, c2):
        dist += bin(b1 ^ b2).count("1")

    total_bits = len(c1) * 8
    percentage = (dist / total_bits) * 100 if total_bits > 0 else 0

    log(f"Avalancha (bits diferentes): {dist} ({percentage:.2f}%)")
    return dist, percentage


# ------------------------------------------
# GRÁFICO 1: HISTOGRAMA DE BYTES
# ------------------------------------------
def plot_histogram(data):
    # Convertir bytes a enteros para evitar errores de unicode
    if isinstance(data, (bytes, bytearray)):
        data = list(data)

    plt.figure()
    plt.hist(data, bins=256)
    plt.title("Histograma de Valores del Cifrado")
    plt.xlabel("Valor (0-255)")
    plt.ylabel("Frecuencia")
    plt.tight_layout()
    plt.savefig("histograma.png")
    plt.close()


# ------------------------------------------
# GRÁFICO 2: AVALANCHA (BARRA)
# ------------------------------------------
def plot_avalanche(values):
    plt.figure(figsize=(6,4))
    plt.bar(range(len(values)), values)
    plt.title("Avalancha")
    plt.xlabel("Prueba")
    plt.ylabel("Bits cambiados")
    outfile = "avalancha.png"
    plt.savefig(outfile)
    plt.close()
    log(f"Gráfico guardado: {outfile}")
