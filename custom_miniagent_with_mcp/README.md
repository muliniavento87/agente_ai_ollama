- Crea server MCP
    - server.py
- Crea mini agente (usa solo i tools di server.py)
    - agente.py
    - carica (automaticamente) da server.py i tools, crea il catalogo e richiama il modello via cURL con la domanda e il catalogo
- Avvia VENV (se già installato)
    - Basta avviare agente.py che avvia dentro anche il server.py da solo
        - unix
        ```bash
        source venv/bin/activate;
        python agente.py
        ```
        - windows (powershell)
        ```PowerShell
        .\venv\Scripts\Activate.ps1;
        python agente.py
        ```
- Installa dipendenze e VENV
    - unix
    ```bash
    python3 -m venv venv;
    source venv/bin/activate;
    pip install requests mcp
    ```
    - windows (powershell)
    ```PowerShell
    python -m venv venv;
    .\venv\Scripts\Activate.ps1;
    pip install requests mcp
    ```