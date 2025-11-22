📘 README – EMO-SPN (Emotional Substitution-Permutation Network)
Autores:

Oscar López, Hannia Tsui, Zanhia Lucero

Materia: Criptografía
Universidad Autónoma de Baja California Sur
⭐ 1. Introducción

El proyecto EMO-SPN implementa un algoritmo criptográfico basado en el modelo clásico Substitution-Permutation Network (SPN), integrando además una variante de sustitución inspirada en emojis y transformaciones no lineales para incrementar la confusión y difusión del mensaje.

El objetivo del proyecto es comprender y aplicar conceptos fundamentales de criptografía moderna, entre ellos:

Cifrado por bloques

Sustitución (S-Box)

Permutación (P-Layer)

Expansión de clave

Métricas criptográficas (entropía, efecto avalancha, histogramas)

Medición de desempeño

⭐ 2. Objetivo del Proyecto

Implementar un cifrador por bloques basado en SPN.

Evaluar el algoritmo utilizando entropía, histograma y efecto avalancha.

Realizar pruebas completas de cifrado/descifrado.

Integrar un sistema de logs y medición de tiempo para evaluar desempeño.

Generar estructuras y funciones modulares que permitan análisis criptográfico.

⭐ 3. Arquitectura del Algoritmo EMO-SPN

El algoritmo sigue una secuencia clásica:

Entrada del mensaje → se transforma a bloques de bytes.

S-Box EMO → tabla no lineal personalizada.

P-Layer → permutación bit a bit para generar difusión.

Rondas SPN → cada ronda aplica:

XOR con subclave

Sustitución (S-Box)

Permutación (P-Layer)

Ronda final

Salida del cifrado

⭐ 4. Diagrama del Algoritmo EMO-SPN

A continuación, el diagrama solicitado (generado por mí, listo para usar):

                     ┌──────────────────┐
                     │  Mensaje (Texto) │
                     └─────────┬────────┘
                               │
                               ▼
                   ┌────────────────────┐
                   │ Conversión a Bytes │
                   └─────────┬──────────┘
                             │
                Bloques de 16 bytes
                             │
                             ▼
             ┌────────────────────────────┐
             │    Ronda 1 a N (SPN)       │
             │  ┌──────────────────────┐  │
             │  │ XOR con Subclave     │  │
             │  ├──────────────────────┤  │
             │  │ Sustitución (S-Box)  │  │
             │  ├──────────────────────┤  │
             │  │ Permutación (P-Layer)│  │
             │  └──────────────────────┘  │
             └───────────┬────────────────┘
                         │
                         ▼
           ┌─────────────────────────┐
           │ Ronda Final (XOR Key)   │
           └──────────┬──────────────┘
                      │
                      ▼
             ┌──────────────────┐
             │ Cifrado (Bytes)  │
             └──────────────────┘

⭐ 5. Funcionalidades Principales
✔ Cifrado y Descifrado

Funciones: emo_encrypt() y emo_decrypt()

Basado completamente en SPN con S-Boxes personalizadas.

✔ Medición de Tiempo

Evaluación del rendimiento con measure_time.

✔ Registro en Consola

Con la función log() para depuración y análisis.

✔ Entropía del Cifrado

Se calcula la entropía Shannon del texto cifrado.

✔ Efecto Avalancha

Se compara el resultado del cifrado al modificar 1 bit del mensaje original.

✔ Gráficos Automáticos

Histograma de distribución de bytes cifrados.

Gráfica del efecto avalancha.

⭐ 6. Estructura del Proyecto
Emo-codigo_v2/
│
├── src/
│   ├── emo_spn.py          # Implementación del cifrador EMO-SPN
│   ├── logging_tools.py    # Logs, métricas y gráficos
│   ├── test.py             # Script principal de pruebas
│
├── README.md               # Este archivo
└── requirements.txt        # Dependencias

⭐ 7. Instrucciones de Uso
1️⃣ Ejecutar pruebas
python src/test.py

2️⃣ Instalar dependencias
pip install -r requirements.txt

3️⃣ Modificar mensaje o clave

En test.py:

mensaje = "Hola EMO-SPN"
clave = "MiClaveSegura123"

⭐ 8. Resultados Esperados

El descifrado debe coincidir exactamente con el mensaje original.

El histograma debe mostrar una distribución uniforme (indicador de buena confusión).

El efecto avalancha debe generar cambios significativos (>40%).

La entropía debe acercarse a valores altos (≈7–8 bits).

⭐ 9. Conclusiones

El algoritmo EMO-SPN implementado ofrece una visión clara del funcionamiento de una red de sustitución-permutación y permite experimentar con conceptos fundamentales de criptografía moderna.
También proporciona herramientas de evaluación que ayudan a medir la seguridad y calidad del cifrado, como entropía, distribución de valores y efecto avalancha.

Se trata de un proyecto educativo diseñado para comprender los pilares de los cifradores por bloques y los principios de confusión y difusión introducidos por Claude Shannon.

⭐ 10. Créditos

Autores:

Oscar López

Hannia Tsui

Zanhãia Lucero
