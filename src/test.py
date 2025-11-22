from emo_spn import emo_encrypt, emo_decrypt
from logging_tools import (
    log, measure_time, compute_entropy, avalanche_distance,
    plot_histogram, plot_avalanche
)

# ------------------------------
# PRUEBA DE CIFRADO Y DESCIFRADO
# ------------------------------
mensaje = "Hola EMO-SPN"
clave = "MiClaveSegura123"

(cifrado, t_enc) = emo_encrypt(mensaje, clave)
(descifrado, t_dec) = emo_decrypt(cifrado, clave)

log(f"Mensaje original: {mensaje}")
log(f"Cifrado (hex): {cifrado.hex()}")
log(f"Descifrado: {descifrado}")

# ------------------------------
# ENTROPÍA
# ------------------------------
entropy = compute_entropy(cifrado)

# ------------------------------
# AVALANCHA
# ------------------------------
mensaje_mod = "Hola EMO-SPl"  # cambia 1 letra
(cifrado_mod, _) = emo_encrypt(mensaje_mod, clave)

avalancha = avalanche_distance(cifrado, cifrado_mod)

# ------------------------------
# GRÁFICOS
# ------------------------------
plot_histogram(cifrado)
plot_avalanche([avalancha])
