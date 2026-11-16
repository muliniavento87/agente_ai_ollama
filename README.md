# Raccolta tools: Agente + Server LLM
Tools:
1. custom_miniagent_with_mcp
2. docker_pi_agent
3. server_edge0_ram_lt_8gb
4. servers_LLM

## 1. custom_miniagent_with_mcp
Creazione Agente che usa esclusivamente tools custom del catalogo.

## 2. docker_pi_agent
Creazione Docker con dentro Agente Pi Agent configurato con plugin, modelli e script di sviluppo.

## 3. server_edge0_ram_lt_8gb
Server\provider leggero Edge0 + modello Edge0 35b (Qwen 3.6 35b, Q3 circa) con streaming SSD per girare su 3-4gb ram/vram.

## 4. server_ollama_fork_ternary
Un fork non ufficiale di Ollama per renderlo compatibile con l'uso di modelli con quantizzazione ternaria q1.58 (-1, 0, +1).
Modelli disponibili (tutti agentici):
- Ternary-Bonsai-2-4B-PTQ1_0.gguf (molto leggero circa 1gb)
- Ternary-Bonsai-2-27B-PTQ1_0.gguf (più potente circa 6 gb)

## 5. servers_LLM
Lista servers/providers di modelli LLM, configurazione e avvio.