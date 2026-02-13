# Proyecto Integrador – Informe Técnico Breve

Carrera: AI Engineering  
Alumno: Diego Lopez Castan  

---


# Arquitectura 

El sistema implementa un asistente estructurado para agentes de soporte al cliente.

## Flujo de ejecución:

1. El usuario envía una pregunta.
2. `run_query.py`:
   - Carga el prompt desde `prompts/main_prompt.txt`
   - Envía la consulta a OpenAI API
3. El modelo devuelve una respuesta en formato JSON.
4. Se valida que sea JSON y que contenga los campos requeridos
5. Se calculan métricas:
   - prompt_tokens
   - completion_tokens
   - total_tokens
   - latency_ms
   - estimated_cost_usd(basado en costo de input y output del modelo)
6. Las métricas se registran en `metrics/metrics.csv`.

---

## Componentes principales

| Componente | Responsabilidad |
|------------|------------------|
| main_prompt.txt | Define comportamiento y formato obligatorio |
| run_query.py | Orquesta la llamada al modelo y captura métricas |
| safety.py | Control básico contra prompt injection |
| metrics.csv | Registro persistente de métricas |
| tests/test_core.py | Validación automatizada del contrato |

---


# Técnica de Prompting Utilizada

## Técnica Principal: Few-Shot Prompting

En `main_prompt.txt` se incluyen ejemplos estructurados para forzar consistencia.

## ¿Por qué Few-Shot?

- Controlo el output
- Reduzco errores de formato

---

## Estrategia de Control

El prompt establece:

- "Responde SIEMPRE y ÚNICAMENTE con JSON válido"
- Formato obligatorio
- Ejemplo explícito de salida correcta

Esto reduce:
- Texto adicional
- Explicaciones no solicitadas
- Formatos incorrectos

---

# Métricas y Resultados de Muestra

Las métricas se registran automáticamente por ejecución y quedan guardadas en el archivo metrics.csv.

## Métricas registradas

- prompt_tokens
- completion_tokens
- total_tokens
- latency_ms
- estimated_cost_usd

---


Ejemplo ejecución:

| Métrica | Valor aproximado |
|----------|------------------|
| prompt_tokens | 120 |
| completion_tokens | 80 |
| total_tokens | 200 |
| latency_ms | 900 – 1100 ms |
| estimated_cost_usd | ~0.002 – 0.003 USD |


Se pueden ver las corridas en el archivo [Ver archivo de métricas](../metrics/metrics.csv)

---

## Observaciones

- La latencia es consistente (< 1.2s)
- El costo por consulta es bajo (menos de 0.000186 USD)


# Mejoras

Algunas de las mejoras que se puede realizar para el proyecto son:
- Crear una versión desacoplada del programa
- Realizar pruebas con otros modelos
- Optimizar el prompt de entrada
- Automatizar el rescate del costo de los modelos de Open AI
- Crear gráfico para verificar comportamientos raros


---

Desarrollado por Diego Lopez Castan
