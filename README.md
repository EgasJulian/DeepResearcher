# LangGraph Research Agent Web Interface

Este proyecto implementa una interfaz web sencilla para interactuar con un agente de investigación basado en LangGraph. Permite a los usuarios iniciar una investigación sobre un tema específico, revisar un plan generado por el agente, aprobarlo o proporcionar feedback para su modificación, y finalmente recibir un informe completo.

El backend está construido con FastAPI (Python) y el frontend es una página HTML estática con JavaScript que utiliza Marked.js para renderizar las respuestas en formato Markdown. Está diseñado pensando en un despliegue sencillo en plataformas como Vercel.

## ✨ Características

* **Interfaz Web Simple:** Introduce un tema y gestiona el flujo de investigación.
* **Backend con FastAPI:** API robusta y asíncrona para manejar las interacciones con LangGraph.
* **Integración con LangGraph:** Orquesta agentes complejos definidos mediante un grafo LangGraph precompilado.
* **Flujo Interactivo:** Maneja interrupciones del agente para solicitar aprobación o feedback sobre planes/esquemas.
* **Renderizado de Markdown:** Muestra los planes y reportes finales con formato profesional usando Marked.js.
* **Listo para Despliegue:** Configurado para despliegues sencillos en servicios PaaS como Vercel.

## 🛠️ Tech Stack

* **Backend:**
    * Python 3.9+
    * FastAPI
    * LangGraph
    * Uvicorn (Servidor ASGI)
    * Pydantic (Validación de datos)
    * python-dotenv (Gestión de variables de entorno)
    * OpenAI, Tavily (o las librerías específicas usadas por tu grafo `builder`)
* **Frontend:**
    * HTML5
    * CSS3
    * JavaScript (Vanilla)
    * Marked.js (Renderizado de Markdown)
* **Despliegue:**
    * Vercel (Plataforma objetivo)

## 📁 Estructura del Proyecto

├── app/                    # Directorio principal de la aplicación FastAPI
│   ├── init.py
│   ├── main.py             # Endpoints FastAPI, CORS, configuración app
│   ├── graph_logic.py      # Lógica de interacción con el grafo LangGraph
│   └── models.py           # Modelos Pydantic para request/response
├── static/                 # Archivos estáticos (frontend)
│   └── index.html          # Interfaz de usuario HTML/CSS/JS
├── .env.example            # Ejemplo de archivo de variables de entorno
├── .gitignore              # Archivos/Directorios ignorados por Git
├── requirements.txt        # Dependencias de Python
├── vercel.json             # Configuración de despliegue para Vercel
└── README.md               # Este archivo

## ⚙️ Prerrequisitos

* Python 3.9 o superior
* `pip` (gestor de paquetes de Python)
* Git (para clonar el repositorio)
* Claves API para los servicios utilizados por tu grafo LangGraph (ej. OpenAI, Tavily).

## 🚀 Configuración Local

1.  **Clonar el Repositorio:**
    ```bash
    git clone <url-del-repositorio>
    cd <nombre-del-directorio>
    ```

2.  **Crear y Activar un Entorno Virtual:**
    ```bash
    python -m venv venv
    # En macOS/Linux:
    source venv/bin/activate
    # En Windows:
    .\venv\Scripts\activate
    ```

3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    *Nota: Asegúrate de que el módulo `open_deep_research` (de donde importas `builder`) esté instalado como paquete o sea accesible en tu PYTHONPATH si es un módulo local.*

4.  **Configurar Variables de Entorno:**
    * Copia el archivo de ejemplo: `cp .env.example .env` (o `copy .env.example .env` en Windows).
    * Edita el archivo `.env` y añade tus claves API:
        ```dotenv
        OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        # Añade otras claves necesarias por tu grafo
        ```
    * **Importante:** El archivo `.env` ya está incluido en `.gitignore` para evitar subir tus claves secretas accidentalmente.

## ▶️ Ejecutar Localmente

1.  **Iniciar el Servidor FastAPI:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    * `--reload`: El servidor se reiniciará automáticamente al detectar cambios en el código.
    * `--host 0.0.0.0`: Hace que el servidor sea accesible desde otras máquinas en tu red local (además de `localhost`).
    * `--port 8000`: Especifica el puerto en el que se ejecutará el servidor.

2.  **Acceder a la Aplicación:**
    Abre tu navegador web y ve a `http://localhost:8000`.

## 💻 Uso

1.  Introduce el tema que deseas investigar en el campo de texto.
2.  Haz clic en "Iniciar Investigación".
3.  Espera a que el agente procese y genere un plan. Este plan se mostrará en formato Markdown.
4.  Revisa el plan:
    * Si estás de acuerdo, haz clic en "Aprobar Plan". El agente continuará para generar el informe final.
    * Si deseas modificar el plan, escribe tus comentarios/sugerencias en el área de texto "Feedback" y haz clic en "Enviar Feedback". El agente intentará actualizar el plan según tus indicaciones y te presentará una nueva versión.
5.  Una vez aprobado el plan final (o si el feedback lleva a la finalización), el agente generará el informe completo, que se mostrará también en formato Markdown.

## 🔗 API Endpoints

La aplicación expone los siguientes endpoints:

* `POST /api/start`: Inicia una nueva ejecución del agente.
    * **Request Body:** `{ "topic": "string" }`
    * **Response Body:** `{ "thread_id": "string", "interrupt_message": "string | null", "status": "string" }`
* `POST /api/resume`: Reanuda una ejecución existente con aprobación o feedback.
    * **Request Body:** `{ "thread_id": "string", "approval": true | null, "feedback": "string | null" }` (solo uno entre `approval` y `feedback` debe estar presente).
    * **Response Body:** `{ "thread_id": "string", "interrupt_message": "string | null", "final_report": "string | null", "status": "string" }`

*(FastAPI también genera automáticamente documentación interactiva de la API en `/docs` y `/redoc` cuando se ejecuta localmente).*

---

¡Siéntete libre de contribuir, reportar bugs o sugerir mejoras!