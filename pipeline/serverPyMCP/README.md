# Server MCP
Server che rispetta lo standard MCP

## Dipendenze
```bash
python3 -m venv venv;
source venv/bin/activate;
pip install mcp
```

## Avvio
Lo fa da solo Pi Agent, specifichiamo solo come chiamarlo in configurazione Pi Agent (in "~/.pi/agent/mcp-adapter.json")
```bash
python3 -m venv venv;
source venv/bin/activate;
python3 server.py
```

## Integrazione Pi Agent
- Installa l'adattatore MCP per Pi Agent
```bash
pi install npm:pi-mcp-adapter
```
- crea configurazione globale per i server MCP (in automatico Pi AGent creerà il catalogo di funzionalità da fornire a Qwen)
```bash
cat << 'EOF' > ~/.pi/agent/mcp.json
{
  "settings": {
    "directTools": true
  },
  "mcpServers": {
    "miei-tool-python": {
      "command": "/workspace/serverPyMCP/venv/bin/python",
      "args": ["/workspace/serverPyMCP/server.py"]
    }
  }
}
EOF
```
