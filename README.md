📘 README – EMO-SPN (Emotional Substitution-Permutation Network)
Autores:

Oscar López, Hannia Tsui, Zanhia Lucero

Materia: Criptografía
Universidad Autónoma de Baja California Sur

Objetivo: Cifrado de bloques de 128 bits con 20 rondas, clave maestra de 256 bits, modo CBC y HMAC-SHA256 para integridad.

Requisitos
- Python 3.10+ (probado en 3.13)
- Paquetes: matplotlib , numpy
- Instalación: pip install matplotlib numpy

Estructura
- src/emo_spn.py : núcleo del cifrado, CLI de archivos, API programática
- src/emo.py : CLI para cifrado/descifrado de mensajes y ejecución de tests
- src/logging_tools.py : métricas y gráficos
- src/sandbox/ : zona segura para archivos de prueba
- escrow/recovery.enc : sobre de recuperación de clave generado por init
- tests/test_emospn.py : tests unitarios

Uso Rápido (API Programática)
- Cifrar: cipher, t = emo_encrypt("Hola EMO-SPN", "MiClaveSegura123")
- Descifrar: plain, t = emo_decrypt(cipher, "MiClaveSegura123")
- Formato de cipher : IV(16) || C || TAG(32) con HMAC-SHA256 sobre IV || C usando la clave maestra derivada de la passphrase

CLI de Mensajes
- Ubicación: src/emo.py
- Cifrar: python src/emo.py encrypt --msg "Hola EMO-SPN" --key "MiClaveSegura123"
- Descifrar: python src/emo.py decrypt --msg "<hex_del_cipher>" --key "MiClaveSegura123"
- Tests: python src/emo.py test

CLI de Archivos y Escrow
- Ubicación: src/emo_spn.py
- Inicializar: python src/emo_spn.py init -p "MiPassphrase"
  - Genera escrow/recovery.enc y sandbox/key.bin.enc
- Cifrar archivo: python src/emo_spn.py encrypt sandbox/sample.txt sandbox/sample.enc -p "MiPassphrase"
- Descifrar archivo: python src/emo_spn.py decrypt sandbox/sample.enc sandbox/sample.dec.txt -p "MiPassphrase"
- Notas:
  - Las rutas deben estar bajo src/sandbox/ por seguridad
  - El formato del archivo cifrado es IV || C || TAG
  - La passphrase destraba el escrow que contiene la clave maestra ofuscada

Pruebas
- Unitarias: python -m unittest -v tests/test_emospn.py
  - Verifica cifrado/descifrado, entropía y avalancha
- Script de métricas: python src/test.py
  - Genera tiempos, gráficos y logs en execution.log

Salida y Métricas
- Logs: execution.log
- Gráficos: histograma.png , avalancha.png
- Métricas:
  - Entropía (Shannon) del ciphertext
  - Avalancha (bits diferentes y porcentaje)
  - Tiempos de cifrado y descifrado con throughput

Detalles Criptográficos
- SPN 20 rondas: SubBytes con S-box derivada por clave, P-layer permutación de bits, AddRoundKey
- Modo CBC con IV aleatorio
- HMAC-SHA256 para autenticidad del ciphertext
- Derivación interna de componentes con PRNG XORShift64 sembrado por SHA-256(master_key||label)

Qué esperar
- Ciphertexts diferentes para mismo mensaje por IV aleatorio
- Entropía alta del cipher (~6.5+ bits/byte)
- Avalancha cercana al 50% de bits cambiados entre mensajes similares

Ejemplos
- Generar clave y cifrar archivo de sandbox:
  - python src/emo_spn.py init -p "MiPassphrase"
  - python src/emo_spn.py encrypt sandbox/sample.txt sandbox/sample.enc -p "MiPassphrase"
  - python src/emo_spn.py decrypt sandbox/sample.enc sandbox/sample.dec.txt -p "MiPassphrase"
  
Ubicaciones clave del código
- SPN cifrado por bloque: src/emo_spn.py:110-116
- SPN descifrado por bloque: src/emo_spn.py:118-125
- CBC archivos: src/emo_spn.py:167-175 y src/emo_spn.py:193-201
- API cifrado/descifrado: src/emo_spn.py:347-383 , src/emo_spn.py:386-424
- Métrica avalancha: src/logging_tools.py:48-57
- Prueba script con tiempos: src/test.py actualizado