# app/graph_logic.py
from openai import OpenAI
import uuid
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from open_deep_research.graph import builder
# Carga variables de entorno (API Keys) desde un archivo .env
# ¡Crea un archivo .env en la raíz del proyecto con tus claves!
# Ejemplo .env:
# OPENAI_API_KEY=sk-xxxxxxxxxx
# TAVILY_API_KEY=tvly-xxxxxxxxxx
load_dotenv()

def translate_to_spanish(text: str) -> str:
    """
    Traduce un texto al español utilizando el modelo GPT-4o de OpenAI.
    
    Args:
        text (str): El texto en inglés que se desea traducir.
    
    Returns:
        str: El texto traducido al español.
    """
    try:        
        
        # Crear una instancia del cliente
        client = OpenAI()
        
        # Llama a la API de OpenAI para realizar la traducción
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a translation assistant. Translate all input to Spanish without changing anything."},
                {"role": "user", "content": text}
            ]
        )
        
        # Extrae la traducción del contenido de la respuesta
        translated_text = response.choices[0].message.content
        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        raise RuntimeError("Failed to translate text to Spanish.") from e

def translate_to_english(text: str) -> str:
    """
    Traduce un texto al inglés utilizando el modelo GPT-4o de OpenAI.
    
    Args:
        text (str): El texto en español que se desea traducir.
    
    Returns:
        str: El texto traducido al inglés
    """
    try:        
        
        # Crear una instancia del cliente
        client = OpenAI()
        
        # Llama a la API de OpenAI para realizar la traducción
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a translation assistant. Translate all input to English without changing anything."},
                {"role": "user", "content": text}
            ]
        )
        
        # Extrae la traducción del contenido de la respuesta
        translated_text = response.choices[0].message.content
        return translated_text
    except Exception as e:
        print(f"Error during translation: {e}")
        raise RuntimeError("Failed to translate text to Spanish.") from e
    
# --- Configuración del Grafo ---
memory = MemorySaver()
# Compila el grafo una vez al iniciar el módulo
try:
    graph = builder.compile(checkpointer=memory)
    print("LangGraph compiled successfully.")
except Exception as e:
    print(f"Error compiling LangGraph: {e}")
    # Puedes decidir si quieres que la app falle al iniciar o manejar esto de otra forma
    raise e # Falla rápido si el grafo no compila
REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:
Introduction (no research needed)
Brief overview of the topic area
Main Body Sections:
Include a maximum of 3 sections, each focusing on a sub-topic of the user-provided topic
AT LEAST ONE section must require research
The remaining sections can be developed with existing knowledge or may also require research depending on the topic
Conclusion
Aim for 1 structural element (either a list of table) that distills the main body sections
Provide a concise summary of the report"""
DEFAULT_THREAD_CONFIG = {
    "search_api": "tavily", # Asegúrate de tener la API Key configurada
    "planner_provider": "openai",
    "planner_model": "gpt-4o", # Asegúrate de tener la API Key configurada
    "writer_provider": "openai",
    "writer_model": "gpt-4o",
    "max_search_depth": 2,
    "report_structure": REPORT_STRUCTURE,
}
# --- Funciones Asíncronas para Interactuar con el Grafo ---
async def start_graph_execution(topic: str, searcher: str) -> tuple[str, str | None]:
    """
    Inicia la ejecución del grafo con un nuevo tema y thread_id.
    Retorna (thread_id, mensaje_interrupcion) o (thread_id, None) si no hay interrupción inicial.
    """
    thread_id = str(uuid.uuid4())
    DEFAULT_THREAD_CONFIG["search_api"] = searcher # Cambia el buscador según la solicitud
    if (searcher == "exa"):
        DEFAULT_THREAD_CONFIG["search_api_config"] = {"num_results": 2}
    thread_config = {"configurable": {"thread_id": thread_id, **DEFAULT_THREAD_CONFIG}}
    interrupt_message = None
    print(f"Starting graph for topic: {translate_to_english(topic)} with thread_id: {thread_id}")
    try:
        async for event in graph.astream({"topic": translate_to_english(topic)}, thread_config, stream_mode="updates"):
            print(f"Event received: {event}") # Debugging
            if '__interrupt__' in event:
                interrupt_value = event['__interrupt__'][0].value
                print(f"Interrupt received for thread {thread_id}: {interrupt_value}")
                interrupt_message = interrupt_value
                # Detener el bucle una vez que se recibe la interrupción
                break # Importante salir después de la primera interrupción
            # Considera manejar otros eventos si es necesario (ej. errores)
            if 'error' in event: # Ejemplo básico de manejo de errores
                print(f"Error event in graph stream: {event['error']}")
                # Podrías querer lanzar una excepción o manejarlo de otra forma
    except Exception as e:
        print(f"Error during graph execution for thread {thread_id}: {e}")
        # Aquí podrías lanzar una excepción HTTP en el endpoint de FastAPI
        raise RuntimeError(f"Graph execution failed for thread {thread_id}") from e

    return thread_id, interrupt_message
async def resume_graph_execution(thread_id: str, resume_input: bool | str) -> tuple[str | None, str | None]:
    """
    Reanuda la ejecución del grafo para un thread_id existente.
    resume_input: True para aprobar, str para dar feedback.
    Retorna (nuevo_mensaje_interrupcion, None) si hay otra interrupción,
            (None, reporte_final) si la ejecución termina.
    """
    thread_config = {"configurable": {"thread_id": thread_id, **DEFAULT_THREAD_CONFIG}}
    if type(resume_input) == str:
        # Si es un feedback, lo transformamos a un comando
        resume_input = translate_to_english(resume_input)
        print(f"Feedback received: {resume_input}")
    command_to_resume = Command(resume=resume_input)
    next_interrupt_message = None
    final_report = None
    print(f"Resuming graph for thread_id: {thread_id} with input type: {resume_input} y el buscador {DEFAULT_THREAD_CONFIG['search_api']}")
    try:
        async for event in graph.astream(command_to_resume, thread_config, stream_mode="updates"):
            print(f"Resume Event received: {event}") # Debugging
            if '__interrupt__' in event:
                interrupt_value = event['__interrupt__'][0].value
                print(f"Interrupt received during resume for thread {thread_id}: {interrupt_value}")
                next_interrupt_message = interrupt_value
                # Detener el bucle en la nueva interrupción (si se dio feedback)
                break
            # Aquí asumimos que si no hay interrupción, el grafo debería terminar.
            # Necesitamos verificar si el grafo ha terminado de otra manera.
            # El stream podría simplemente terminar sin un evento 'interrupt' si se aprueba.

        # Después de que el stream termina (ya sea por interrupción o finalización):
        if not next_interrupt_message:
            # Si no hubo una nueva interrupción, intentamos obtener el estado final
            print(f"Stream finished for thread {thread_id}. Checking final state.")
            final_state = await graph.aget_state(thread_config) # Usar aget_state para async
            # Ajusta la clave según cómo tu grafo almacena el reporte final
            final_report = final_state.values.get('final_report')
            if final_report:
                print(f"Final report retrieved for thread {thread_id}")
            else:
                print(f"Stream finished but no final report found in state for thread {thread_id}. State: {final_state.values.keys()}")
                # Podría ser un error o un estado intermedio no esperado
    except Exception as e:
        print(f"Error during graph resume for thread {thread_id}: {e}")
        # Manejar el error, posiblemente lanzar una excepción HTTP
        raise RuntimeError(f"Graph resume failed for thread {thread_id}") from e

    return next_interrupt_message, final_report