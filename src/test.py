from emo_spn import emo_encrypt, emo_decrypt
from logging_tools import (
    log, avalanche_distance,
    plot_histogram, plot_avalanche,
    compute_entropy_value, plot_performance_entropy
)

# ------------------------------
# PRUEBA DE CIFRADO Y DESCIFRADO
# ------------------------------
mensaje = "Hola EMO-SPN esta prueba es para ver que tanto cambia si uso una cara triste o feliz :)"
clave = "MiClaveSegura123"

(cifrado, t_enc) = emo_encrypt(mensaje, clave)
(descifrado, t_dec) = emo_decrypt(cifrado, clave)

log(f"Mensaje original: {mensaje}")
log(f"Cifrado (hex): {cifrado.hex()}")
log(f"Descifrado: {descifrado}")
log(f"Tiempo cifrado: {t_enc:.6f}s | Tamaño: {len(cifrado)} bytes | Throughput: {len(cifrado)/t_enc/1000:.2f} KB/s")
log(f"Tiempo descifrado: {t_dec:.6f}s | Tamaño: {len(cifrado)} bytes | Throughput: {len(cifrado)/t_dec/1000:.2f} KB/s")

# ------------------------------
# ENTROPÍA
# ------------------------------
# La entropía detallada se imprimirá al final en un solo bloque

# ------------------------------
# AVALANCHA
# ------------------------------
mensaje_mod = "Hola EMO-SPN esta prueba es para ver que tanto cambia si uso una cara triste o feliz :("
(cifrado_mod, _) = emo_encrypt(mensaje_mod, clave)

avalancha_bits, avalancha_pct = avalanche_distance(cifrado, cifrado_mod)
log(f"Avalancha total (bits distintos): {avalancha_bits} ({avalancha_pct:.2f}%)")


# ------------------------------
# GRÁFICOS
# ------------------------------
plot_histogram(cifrado)
plot_avalanche([avalancha_bits])

sizes = [16, 64, 256, 1024, 4096]
perf_rows = []
entropy_rows = []
for s in sizes:
    msg = "A" * s
    c, te = emo_encrypt(msg, clave)
    p, td = emo_decrypt(c, clave)
    ent = compute_entropy_value(c)
    perf_rows.append([s, te, td, len(c)/te/1000, len(c)/td/1000])
    entropy_rows.append([s, ent])

# Tabla combinada (performance y entropía)
plot_performance_entropy(perf_rows, entropy_rows)

# Resumen de entropía único
overall_entropy = compute_entropy_value(cifrado)
log(f"Entropía del texto cifrado (archivo completo): {overall_entropy:.4f} bits/byte")
log("")
log("Entropía por bloque:")
c_body = cifrado[16:-32]
num_blocks = min(5, len(c_body)//16)
for i in range(num_blocks):
    b = c_body[i*16:(i+1)*16]
    e = compute_entropy_value(b)
    log(f"  - Bloque {i+1}: {e:.4f}")


