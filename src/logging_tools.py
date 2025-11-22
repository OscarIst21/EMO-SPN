import logging
import time
import math
import matplotlib.pyplot as plt
from collections import Counter

# ===========================
# CONFIGURACIÓN DE LOGS
# ===========================
logging.basicConfig(
    filename="execution.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)

# ===========================
# MEDIR TIEMPOS
# ===========================
def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        output = func(*args, **kwargs)
        end = time.time()
        elapsed = end - start
        logging.info(f"Tiempo de ejecución ({func.__name__}): {elapsed:.6f} s")
        return output, elapsed
    return wrapper

# ===========================
# ENTROPÍA SHANNON
# ===========================
def compute_entropy(data: bytes):
    if not data:
        return 0.0

    freq = Counter(data)
    total = len(data)
    entropy = -sum((count / total) * math.log2(count / total) for count in freq.values())
    logging.info(f"Entropía Shannon: {entropy:.6f} bits")
    return entropy

# ===========================
# EFECTO AVALANCHA
# ===========================
def avalanche_distance(a: bytes, b: bytes):
    diff_bits = 0

    for x, y in zip(a, b):
        xor_val = x ^ y
        diff_bits += bin(xor_val).count("1")

    total_bits = len(a) * 8
    avalanche = diff_bits / total_bits

    logging.info(f"Avalancha: {avalanche * 100:.2f}% diferencia")
    return avalanche

# ===========================
# GRÁFICOS
# ===========================
def plot_histogram(cipher_bytes: bytes, filename="hist_cipher.png"):
    """
    Genera un histograma de frecuencias de bytes del ciphertext (0–255).
    Soluciona el error de Unicode categórico forzando datos numéricos.
    """
    plt.figure(figsize=(8, 5))

    # Fuerza lista de enteros (0-255) para evitar eje categórico
    data = list(cipher_bytes)

    plt.hist(data, bins=256, range=(0, 255), density=True)

    plt.title("Distribución de bytes del ciphertext")
    plt.xlabel("Valor de byte (0-255)")
    plt.ylabel("Frecuencia normalizada")

    # Forzar el eje X a valores numéricos — evita decodificación UTF-8
    plt.gca().set_xticks(range(0, 256, 32))  
    plt.gca().set_xlim(0, 255)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def plot_avalanche(values, filename="avalancha.png"):
    plt.figure(figsize=(8, 4))
    plt.plot(values, marker="o")
    plt.title("Efecto Avalancha por ronda")
    plt.xlabel("Prueba")
    plt.ylabel("Porcentaje de bits cambiados")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    logging.info(f"Grafica de avalancha generada: {filename}")
