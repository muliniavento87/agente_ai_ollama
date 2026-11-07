import json
import requests
from rich import print
from rich.markdown import Markdown
# Importiamo direttamente dal tuo server automatizzato!
from server import AVAILABLE_TOOLS, get_openai_tools_definition


debug = False

addr_edge0_server = '127.0.0.1:8080'
addr_ollama_server = '127.0.0.1:11434'

server_addr = addr_edge0_server


# Il catalogo viene generato al volo dal server
tools_definition = get_openai_tools_definition()

if debug:
    print("Cataloghi dei tool generati automaticamente dal server:")
    print(json.dumps(tools_definition, indent=2, ensure_ascii=False))

# Messaggi iniziali dell'agente
"""
messages = [
    {
        "role": "system",
        "content": "Sei un assistente efficiente. Hai accesso a dei tool per gestire un diario di task."
    },
    {
        "role": "user",
        "content": "Crea un task nel diario con descrizione: Sviluppare il modulo di login."
    }
]
"""
messages = [
    {
        "role": "system",
        "content": "Sei un assistente efficiente. Hai accesso a dei tool."
    },
    {
        "role": "user",
        "OLDcontent": "Crea un task nel diario con descrizione: Sviluppare il modulo di login.",
        "content": "Quanti pianeti ha il sistema solare?"
    }
]


#print("\n>> Domanda utente:")
#print(f"{messages[1]["content"]}")
while True:
    try:
        testo = input("\n>> Domanda utente: ")
        messages[1]["content"] = testo

        # Chiamata al modello locale passando i tool dinamici
        response = requests.post("http://127.0.0.1:8080/v1/chat/completions", json={
            "model": "edge0-35b",
            "messages": messages,
            "tools": tools_definition,
            "tool_choice": "auto"
        })

        response_data = response.json()
        message = response_data["choices"][0]["message"]
        messages.append(message)

        # Gestione dell'esecuzione automatica del tool richiesto dall'LLM
        if "tool_calls" in message and message["tool_calls"]:
            for tool_call in message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])

                if debug:
                    print(f"\n-> Il modello vuole eseguire: {func_name} con argomenti: {func_args}")
                
                if func_name in AVAILABLE_TOOLS:
                    # Esegue la funzione presa direttamente dal dizionario del server
                    tool_result = AVAILABLE_TOOLS[func_name](**func_args)
                    if debug:
                        print(f"<- Risultato ottenuto: {tool_result}")
                    
                    # Restituisce il risultato al modello
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": func_name,
                        "content": str(tool_result)
                    })
                    
                    # Seconda chiamata per ottenere la risposta finale testuale
                    final_response = requests.post(f"http://{server_addr}/v1/chat/completions", json={
                        "model": "edge0-35b",
                        "messages": messages
                    })

                    response_data = final_response.json()

        print("\n>> Risposta finale dell'agente:")
        resp = response_data["choices"][0]["message"]["content"]
        print(Markdown(resp))

    except KeyboardInterrupt:
        print("\nInterruzione (CTRL+C): Chiusura del programma in corso...")
        exit(0)
