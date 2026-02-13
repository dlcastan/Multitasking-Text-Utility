import json
import time
import csv
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from safety import es_prompt_adversarial
import argparse
import logging

# =========================
# Configuración general
# =========================
MODEL = "gpt-4.1-mini"
COSTO_USD_POR_1K_TOKENS = 0.00015  # estimado, documentado

load_dotenv()
client = OpenAI()

# =========================
# Entrada del usuario
# =========================
PREGUNTA_USUARIO = "La aplicación se cae cuando intento pagar."

if es_prompt_adversarial(PREGUNTA_USUARIO):
    raise ValueError("Entrada bloqueada por posible intento de prompt injection.")

# =========================
# Prompt (few-shot)
# =========================
SYSTEM_PROMPT = """
Eres un asistente de soporte al cliente.
Responde SIEMPRE y ÚNICAMENTE con JSON válido.

El JSON debe tener el siguiente formato:
{
  "answer": string,
  "confidence": number entre 0 y 1,
  "actions": array de strings
}
"""

EJEMPLO_FEW_SHOT = [
    {
        "role": "user",
        "content": "¿Cómo puedo restablecer mi contraseña?"
    },
    {
        "role": "assistant",
        "content": (
            '{"answer":"Puedes restablecer tu contraseña usando el enlace de recuperación en la página de inicio de sesión.",'
            '"confidence":0.90,'
            '"actions":["Dirigir al usuario a la página de recuperación","Sugerir revisar la carpeta de spam"]}'
        )
    }
]

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    *EJEMPLO_FEW_SHOT,
    {"role": "user", "content": PREGUNTA_USUARIO}
]

# =========================
# Ejecución y métricas
# =========================
inicio = time.time()

resp = client.responses.create(
    model=MODEL,
    input=messages,
    temperature=0.2,
    max_output_tokens=150
)

latencia_ms = int((time.time() - inicio) * 1000)

# =========================
# Parseo seguro del JSON
# =========================
salida_raw = resp.output_text.strip()
respuesta = json.loads(salida_raw)

# =========================
# Métricas de uso
# =========================
uso = resp.usage
tokens_prompt = uso.input_tokens
tokens_completion = uso.output_tokens
tokens_totales = uso.total_tokens

costo_estimado = (tokens_totales / 1000) * COSTO_USD_POR_1K_TOKENS

# =========================
# Registro en CSV
# =========================
ruta_metrics = Path("metrics/metrics.csv")
ruta_metrics.parent.mkdir(exist_ok=True)

fila = {
    "timestamp": datetime.utcnow().isoformat(),
    "tokens_prompt": tokens_prompt,
    "tokens_completion": tokens_completion,
    "total_tokens": tokens_totales,
    "latency_ms": latencia_ms,
    "estimated_cost_usd": float(f"{costo_estimado:.6f}")
}

escribir_header = not ruta_metrics.exists()

with open(ruta_metrics, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fila.keys())
    if escribir_header:
        writer.writeheader()
    writer.writerow(fila)

# =========================
# Salida final
# =========================
resultado = {
    "response": respuesta,
    "metrics": {
        **fila,
        "estimated_cost_usd": f"{fila['estimated_cost_usd']:.6f}"
    }
}

print(json.dumps(resultado, indent=2, ensure_ascii=False))
