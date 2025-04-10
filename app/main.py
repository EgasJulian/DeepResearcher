# app/main.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware # Para permitir peticiones del frontend
from .models import StartRequest, StartResponse, ResumeRequest, ResumeResponse
from .graph_logic import start_graph_execution, resume_graph_execution, translate_to_spanish # Importa el grafo compilado

# --- Configuración de FastAPI ---
app = FastAPI(title="LangGraph Agent API", version="0.1.0")
# --- CORS ---
# Ajusta origins según dónde desplegarás tu frontend. '*' es permisivo para desarrollo.
# Para producción, sé más específico: ["https://tu-dominio.com"]
origins = [
    "http://localhost", # Si sirves index.html localmente
    "http://localhost:8000", # Si usas 'python -m http.server'
    "null", # Necesario para archivos locales abiertos directamente en el navegador
    # Añade aquí la URL de tu despliegue en Vercel/Netlify si es diferente
    # "https://<tu-proyecto>.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, etc.
    allow_headers=["*"],
)
# --- Endpoints de la API ---
@app.post("/api/start", response_model=StartResponse)
async def start_agent(request: StartRequest):
    """
    Endpoint para iniciar una nueva ejecución del agente con un tema.
    """
    try:
        print(f"Received start request for topic: {request.topic}")
        thread_id, interrupt_message = await start_graph_execution(request.topic)
        interrupt_message = translate_to_spanish(interrupt_message)
        if interrupt_message is None:
             # Esto no debería pasar según tu descripción, pero manejémoslo
             print(f"Warning: Graph started for thread {thread_id} but no initial interrupt received.")
             # Podrías decidir devolver un error o un estado diferente
             return StartResponse(thread_id=thread_id, interrupt_message="Graph started, waiting for processing.", status="Processing")
        return StartResponse(thread_id=thread_id, interrupt_message=interrupt_message)
    except Exception as e:
        print(f"Error in /api/start: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start graph execution: {str(e)}")

@app.post("/api/resume", response_model=ResumeResponse)
async def resume_agent(request: ResumeRequest):
    """
    Endpoint para reanudar la ejecución del agente con aprobación o feedback.
    """
    if request.approval is None and request.feedback is None:
        raise HTTPException(status_code=400, detail="Must provide either 'approval' (true) or 'feedback' (string).")
    if request.approval is not None and request.feedback is not None:
        raise HTTPException(status_code=400, detail="Cannot provide both 'approval' and 'feedback'.")

    resume_input = request.approval if request.approval is not None else request.feedback
    print(f"Received resume request for thread: {request.thread_id} with input: {resume_input}")

    try:
        interrupt_message, final_report = await resume_graph_execution(request.thread_id, resume_input)

        if final_report:
            final_report = translate_to_spanish(final_report)
            return ResumeResponse(thread_id=request.thread_id, final_report=final_report, status="Completed")
        elif interrupt_message:
            interrupt_message = translate_to_spanish(interrupt_message)
            return ResumeResponse(thread_id=request.thread_id, interrupt_message=interrupt_message, status="Interrupt received")
        else:
            # Caso inesperado: ni interrupción ni reporte final
             print(f"Warning: Resume for thread {request.thread_id} finished without interrupt or final report.")
             # Devuelve un estado indicando que algo inusual ocurrió
             # O intenta obtener el estado de nuevo por si acaso
             # final_state = await graph.aget_state({"configurable": {"thread_id": request.thread_id}})
             # final_report = final_state.values.get('final_report')
             # if final_report:
             #    return ResumeResponse(thread_id=request.thread_id, final_report=final_report, status="Completed")

             # Si aún no hay reporte, informa que está procesando o error
             raise HTTPException(status_code=500, detail="Graph finished processing but no final report or interrupt was found.")

    except Exception as e:
        print(f"Error in /api/resume for thread {request.thread_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resume graph execution: {str(e)}")

# --- Servir el Frontend Estático ---
# Monta el directorio 'static' en la raíz '/'
# Esto significa que 'index.html' será accesible en http://localhost:8000/
# Asegúrate de que esta ruta coincida con cómo Vercel servirá los archivos estáticos
# (Vercel normalmente maneja esto automáticamente si tienes 'static' o 'public')
app.mount("/", StaticFiles(directory="static", html=True), name="static")
# Ruta explícita para servir index.html desde la raíz (opcional si StaticFiles(html=True) funciona)
# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     # Intenta leer el archivo index.html
#     try:
#         with open("static/index.html", "r", encoding="utf-8") as f:
#             html_content = f.read()
#         return HTMLResponse(content=html_content, status_code=200)
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="index.html not found")
# --- Punto de entrada para Uvicorn (si ejecutas directamente python app/main.py) ---
# No es necesario para Vercel, que usará 'uvicorn app.main:app'
if __name__ == "__main__":
    import uvicorn
    # Lee el puerto de la variable de entorno PORT, default a 8000 (común en Vercel/Cloud Run)
    port = int(os.environ.get("PORT", 8000))
    # Escucha en 0.0.0.0 para ser accesible externamente (necesario para contenedores/Vercel)
    uvicorn.run(app, host="0.0.0.0", port=port)
