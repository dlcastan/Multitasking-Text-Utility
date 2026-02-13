import json
import time
import csv
import argparse
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from .safety import es_prompt_adversarial


# =========================
# Configuración global
# =========================
MODEL = "gpt-4.1-mini"

load_dotenv()
client = OpenAI()

#========================================#
# -----      Logger Configuration    ----#
#========================================#

class ColoredFormatter(logging.Formatter):
    """
    Formatea los mensajes de log con los siguientes colors:
    - INFO: Verde
    - WARNING: Amarillo
    - ERROR: Rojo
    """

    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    RESET = "\x1b[0m"
    format_str = "%(asctime)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.INFO: GREEN + format_str + RESET,
        logging.WARNING: YELLOW + format_str + RESET,
        logging.ERROR: RED + format_str + RESET,
    }

    def format(self, record):
        """
        Formatea el registro de log aplicando color según el nivel.

        :param record: Registro de logging.
        :return: String formateado con colores ANSI.
        """
        log_fmt = self.FORMATS.get(record.levelno, self.format_str)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)


logger = logging.getLogger()

if not logger.handlers:
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(ColoredFormatter())
    logger.addHandler(ch)

# -----------------------------
# Cargar prompt externo
# -----------------------------

def load_main_prompt():
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "main_prompt.txt"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

# =========================
# Validación de entrada
# =========================
def validar_entrada(texto: str):
    """
    Valida que la entrada del usuario no sea un intento de prompt injection.

    :param texto: Texto ingresado por el usuario.
    :raises ValueError: Si se detecta un intento adversarial.
    """
    logger.info("Validando si la entrada es segura...")
    if es_prompt_adversarial(texto):
        logger.error("Entrada bloqueada por posible prompt injection.")
        raise ValueError("Entrada bloqueada por posible intento de prompt injection.")


# =========================
# Construcción del prompt
# =========================
def construir_messages(pregunta: str):
    """
    Construye la estructura de mensajes para enviar al modelo.

    Incluye:
    - Prompt del sistema con instrucciones estrictas de formato JSON
    - Ejemplo few-shot
    - Pregunta final del usuario

    :param pregunta: Texto final que se enviará al modelo.
    :return: Lista de mensajes estructurados para la API.
    """

    system_prompt = load_main_prompt()


    ejemplo_few_shot = [
        {
            "role": "user",
            "content": "¿Cómo puedo restablecer mi contraseña?"
        },
        {
            "role": "assistant",
            "content": (
                '{"answer":"Puedes restablecer tu contraseña usando el enlace de recuperación en la página de inicio de sesión.",'
                '"actions":["Dirigir al usuario a la página de recuperación","Sugerir revisar la carpeta de spam"]}'
            )
        }
    ]

    logger.info("Construyendo mensajes para el modelo...")

    return [
        {"role": "system", "content": system_prompt},
        *ejemplo_few_shot,
        {"role": "user", "content": pregunta}
    ]


# =========================
# Ejecución del modelo
# =========================
def ejecutar_modelo(messages):
    """
    Envía la solicitud al modelo de OpenAI y mide la latencia.

    :param messages: Lista de mensajes estructurados.
    :return: Tupla (respuesta API, latencia en milisegundos).
    """
    logger.info("Llamando al modelo...")

    inicio = time.time()

    resp = client.responses.create(
        model=MODEL,
        input=messages,
        temperature=0.2,
        max_output_tokens=150
    )

    latencia_ms = int((time.time() - inicio) * 1000)
    logger.info(f"Modelo respondió en {latencia_ms} ms")

    return resp, latencia_ms


# =========================
# Parseo seguro
# =========================
def parsear_respuesta(resp):
    """
    Parsea la respuesta del modelo asegurando que sea JSON válido.

    :param resp: Objeto respuesta devuelto por la API.
    :return: Diccionario parseado.
    :raises JSONDecodeError: Si la respuesta no es JSON válido.
    """
    salida_raw = resp.output_text.strip()

    try:
        logger.info("Parseando respuesta JSON...")
        return json.loads(salida_raw)
    except json.JSONDecodeError:
        logger.error("La respuesta del modelo no es JSON válido.")
        logger.error(f"Respuesta cruda: {salida_raw}")
        raise


# =========================
# Métricas
# =========================
def calcular_metricas(resp, latencia_ms):
    """
    Calcula métricas de uso del modelo, incluyendo
    un cálculo de costo por token basado en precios 
    de GPT-4.1-mini (input $0.40/M, output $1.60/M).
    """

    uso = resp.usage

    # Tokens de entrada y salida
    tokens_prompt = uso.input_tokens
    tokens_completion = uso.output_tokens

    # Precios por millones de tokens (GPT-4.1-mini)
    costo_por_million_input = 0.40
    costo_por_million_output = 1.60

    # Costo estimado real
    costo_estimado = (
        (tokens_prompt / 1_000_000) * costo_por_million_input +
        (tokens_completion / 1_000_000) * costo_por_million_output
    )

    fila = {
        "timestamp": datetime.utcnow().isoformat(),
        "tokens_prompt": tokens_prompt,
        "tokens_completion": tokens_completion,
        "total_tokens": uso.total_tokens,
        "latency_ms": latencia_ms,
        "estimated_cost_usd": float(f"{costo_estimado:.6f}")
    }

    logger.info(f"Tokens de input: {tokens_prompt}")
    logger.info(f"Tokens de output: {tokens_completion}")
    logger.info(f"Costo estimado: ${fila['estimated_cost_usd']} USD")

    return fila


# =========================
# Registro CSV
# =========================
def registrar_metricas_csv(fila, ruta="metrics/metrics.csv"):
    """
    Registra las métricas en un archivo CSV.

    :param fila: Diccionario con métricas.
    :param ruta: Ruta del archivo CSV.
    """
    ruta_metrics = Path(ruta)
    ruta_metrics.parent.mkdir(exist_ok=True)

    escribir_header = not ruta_metrics.exists()

    with open(ruta_metrics, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fila.keys())
        if escribir_header:
            writer.writeheader()
        writer.writerow(fila)

    logger.info("Métricas registradas en CSV.")


# =========================
# Resultado final
# =========================
def construir_resultado(respuesta, metricas):
    """
    Construye el objeto final de salida.

    :param respuesta: Respuesta JSON del modelo.
    :param metricas: Métricas calculadas.
    :return: Diccionario final serializable.
    """
    return {
        "response": respuesta,
        "metrics": {
            **metricas,
            "estimated_cost_usd": f"{metricas['estimated_cost_usd']:.6f}"
        }
    }


# =========================
# Argument Parsing
# =========================
def parsear_argumentos():
    """
    Parsea argumentos desde línea de comandos.

    Requiere:
    - --pregunta

    :return: Namespace con argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="Ejecuta el workflow de Agentes de IA."
    )

    parser.add_argument(
        "--pregunta",
        type=str,
        required=True,
        help="Pregunta directa del usuario"
    )

    return parser.parse_args()


# =========================
# MAIN
# =========================
def main():
    """
    Main del programa. Orquesta todo el flujo de ejecución.
    Flujo-> Carga argumentos -> Valida -> Ejecuta modelo -> Trae métricas -> Registra -> Imprime resultado
    Punto de entrada principal del programa.
    """
    try:
        args = parsear_argumentos()

        pregunta = args.pregunta 

        logger.info(f"Input final usado: {pregunta}")

        validar_entrada(pregunta)

        messages = construir_messages(pregunta)

        resp, latencia_ms = ejecutar_modelo(messages)

        respuesta_json = parsear_respuesta(resp)

        metricas = calcular_metricas(resp, latencia_ms)

        registrar_metricas_csv(metricas)

        resultado = construir_resultado(respuesta_json, metricas)

        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Error en ejecución: {str(e)}")
        raise


if __name__ == "__main__":
    main()
