# Proyecto Integrador I de Henry

Carrera: AI Engineering  
Alumno: Diego Lopez Castan

Este repositorio contiene los tres primeros proyectos de la carrera de Data Engineer de Henry. 

# 🧠 Multitasking Text Utility – OpenAI API

## 📌 Contexto

Este proyecto implementa una aplicación mínima orientada a producto que funciona como **asistente para agentes de soporte al cliente**.  
El sistema recibe una pregunta del usuario y devuelve una **respuesta estructurada en JSON**, diseñada para ser consumida por sistemas downstream (dashboards, CRM, workflows automáticos, etc.).

Además de la respuesta, el sistema **registra métricas clave por consulta** (tokens, latencia y costo estimado), permitiendo monitorear uso, performance y costos operativos.

---

## 🎯 Objetivos del Proyecto

El objetivo principal es construir un **contrato estable de salida** y demostrar buenas prácticas en el desarrollo de aplicaciones con LLMs.

### Qué se entrega y por qué importa

- **Endpoint o script ejecutable** que:
  - Recibe una pregunta del usuario.
  - Devuelve **JSON válido** con campos bien definidos:
    - `answer`
    - `confidence`
    - `actions`
    - `metrics`
- **Registro de métricas por ejecución**:
  - `prompt_tokens`
  - `completion_tokens`
  - `total_tokens`
  - `latency_ms`
  - `estimated_cost_usd`
- **Aplicación explícita de una técnica de prompt engineering**, documentada y justificada.
- **Reporte técnico breve (1–2 páginas)** describiendo:
  - Arquitectura
  - Técnica de prompting
  - Ejemplos de métricas
  - Trade-offs
- **Al menos un test automatizado** (validación de JSON, métricas o tokens).
- **(Opcional)** Manejo de prompts adversariales / fallback de seguridad.

---

## 🧩 Arquitectura General

```
User Question
   ↓
Prompt Builder (Prompt Engineering)
   ↓
OpenAI API
   ↓
Structured JSON Response
   ↓
Metrics Logger
```

---

## 🧪 Técnica de Prompt Engineering

### Técnica elegida: **Few-Shot Prompting**

Se utiliza **few-shot prompting** para mostrarle explícitamente al modelo ejemplos de entrada y salida esperadas en formato JSON.

**¿Por qué esta técnica?**

- Reduce variabilidad en la estructura del output.
- Mejora la consistencia del formato JSON.
- Facilita integraciones downstream.
- Es simple, efectiva y fácil de mantener en equipos pequeños.

---

## 📦 Formato de Respuesta (Contrato JSON)

```json
{
  "answer": "Puedes restablecer tu contraseña desde la página de inicio de sesión.",
  "confidence": 0.87,
  "actions": [
    "Enviar enlace de recuperación",
    "Escalar a soporte humano si falla"
  ],
  "metrics": {
    "prompt_tokens": 120,
    "completion_tokens": 80,
    "total_tokens": 200,
    "latency_ms": 950,
    "estimated_cost_usd": 0.0024
  }
}
```

---

## 📊 Métricas Registradas

- Prompt tokens  
- Completion tokens  
- Total tokens  
- Latencia en milisegundos  
- Costo estimado en USD  

---

## 🧪 Testing

Incluye tests automatizados para validar:

- JSON válido
- Presencia de campos obligatorios
- Métricas numéricas consistentes

---

## 🛡️ Seguridad (Bonus)

Manejo opcional de prompts adversariales (prompt injection, requests fuera de dominio), manteniendo siempre el contrato JSON.

---

## 🚀 Ejecución

### Requisitos
- Python 3.9+
- OpenAI API Key

### Instalación
```bash
pip install -r requirements.txt
```

### Ejecución
```bash
python main.py
```

---

## 📄 Reporte Técnico

El proyecto incluye un reporte breve (1–2 páginas) con arquitectura, prompting, métricas y trade-offs.

---

## 📌 Conclusión

Este proyecto demuestra buenas prácticas para construir sistemas de IA confiables, observables y escalables, sirviendo como base para futuras extensiones como RAG o agentes inteligentes.
