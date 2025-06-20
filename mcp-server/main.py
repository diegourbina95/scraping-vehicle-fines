from fastmcp import FastMCP
import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path  # python3 only

mcp = FastMCP(name="ScrapingVehicleFinesServer")

mcp_with_instructions = FastMCP(
    name="HelpfulAssistant",
    instructions="""
        Este servidor provee herramientas para scraping de papeletas tanto de Lima como de Callao 
        Llama a fines_lima_by_plate() para obtener información de papeletas lima por placa
        Llama a fines_lima_by_document() para obtener información de papeletas lima por documento de identidad
    """,
)

@mcp.tool
def fines_lima_by_plate(plate: str) -> str:
    try:
        payload = {
            "placa": plate
        }
        payload_json = json.dumps(payload)
        response = requests.post(
            f"{os.getenv('URL_BASE_SCRAPING')}/ms/scrappers/v2.0/papeletas/lima", 
            data=payload_json, 
            headers={"Content-Type": "application/json"})
        
        response.raise_for_status()
        return response.json()  # Devuelve el JSON directamente
        
    except Exception as e:
        return f"Error: {str(e)}, Respuesta: {response.text}"

@mcp.tool
def fines_lima_by_document(document: str) -> str:
    try:
        payload = {
            "documento": document
        }
        payload_json = json.dumps(payload)
        response = requests.post(
            f"{os.getenv('URL_BASE_SCRAPING')}/ms/scrappers/v2.0/papeletas/lima/documento", 
            data=payload_json, 
            headers={"Content-Type": "application/json"})
        
        response.raise_for_status()
        return response.json()  # Devuelve el JSON directamente
        
    except Exception as e:
        return f"Error: {str(e)}, Respuesta: {response.text}"

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=4200,
        path="/scraping-vehicle-fines",
        log_level="debug",)