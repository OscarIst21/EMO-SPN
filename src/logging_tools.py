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

def compute_entropy_value(data: bytes):
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

def plot_performance_entropy(perf_rows, entropy_rows, outfile="perf_entropy.png"):
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    axs[0].axis('off')
    axs[1].axis('off')
    perf_cols = ["Tamaño", "Cifrado (s)", "Descifrado (s)", "KB/s cifrado", "KB/s descifrado"]
    perf_cells = [[f"{r[0]}", f"{r[1]:.6f}", f"{r[2]:.6f}", f"{r[3]:.2f}", f"{r[4]:.2f}"] for r in perf_rows]
    t1 = axs[0].table(cellText=perf_cells, colLabels=perf_cols, loc='center', colWidths=[0.2,0.2,0.2,0.2,0.2])
    t1.auto_set_font_size(False)
    t1.set_fontsize(12)
    t1.scale(1.2, 1.6)
    axs[0].set_title("Performance")
    ent_cols = ["Tamaño", "Entropía (bits/byte)"]
    ent_cells = [[f"{r[0]}", f"{r[1]:.4f}"] for r in entropy_rows]
    t2 = axs[1].table(cellText=ent_cells, colLabels=ent_cols, loc='center', colWidths=[0.3,0.7])
    t2.auto_set_font_size(False)
    t2.set_fontsize(12)
    t2.scale(1.2, 1.6)
    axs[1].set_title("Entropía")
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    log(f"Gráfico guardado: {outfile}")
