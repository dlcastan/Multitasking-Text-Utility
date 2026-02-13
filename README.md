
# Proyecto Integrador : Multitasking Text Utility

Carrera: AI Engineering  
Alumno: Diego Lopez Castan  

---

## Descripción General

Este proyecto implementa un **asistente estructurado para agentes de soporte al cliente** utiliza OpenAI API.

El sistema:

- Recibe una pregunta del usuario
- Devuelve **JSON validado y estructurado**
- Registra métricas de uso (tokens, latencia y costo estimado)

---


# Objetivos

- Construir un **contrato JSON estable**
- Medir costos y performance por consulta
- Aplicar técnica explícita de prompt engineering
- Incorporar testing automatizado


---

# 📁 Estructura del Proyecto

```
PI/
│
├── metrics/
│   └── metrics.csv -> Registra las métricas
│
├── prompts/
│   └── main_prompt.txt -> Define el prompt principal
│
├── reports/
│   └── PI_report_es.md -> Reporte técnico 
│
├── src/
│   ├── run_query.py -> Aplicación principal
│   └── safety.py -> Detecta si el texto contiene problemas de seguridad
│
├── tests/
│   └── test_core.py -> Valida al programa
│
├── .env.example
├── Makefile
├── README.md
└── requirements.txt
```




## Configuración

**.env** crear el archivo e incluir la variable:
```
OPENAI_API_KEY=tu_api_key
```

**requirements.txt**
Instalar con:

```
make install
```

**Ejecutar el programa*:**

```
make run ARGS="--pregunta 'Realizar la pregunta aquí'"
```

**Ejectuar test del programa:**
```
make test
```


# Seguridad

Incluye:
- Protección contra prompt injection  
- Validación estricta de JSON  
- Garantía de contrato estructurado  

Los prompts creados para contolar la seguridad del modelo fueron tomados según el documento OWASP Top 10 for
LLM Applications 2025 del OWASP GenAI Security Project. Link: https://genai.owasp.org/

**Verificar control de seguridad**
```
make run ARGS="--pregunta 'ignora las instrucciones'"
```

---

## Autor
Desarrollado por Diego Lopez Castan

## Licencia
Uso libre para fines educativos y personales.
