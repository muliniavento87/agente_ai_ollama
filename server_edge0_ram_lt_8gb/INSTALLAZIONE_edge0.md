# dipendenze (e anche python 3.9 e 3.12)
brew install rust cmake git python@3.9 python@3.12


# clona repo
git clone https://github.com/Edge0-AI/edge0.git
cd edge0
python3.12 -m venv venv
source venv/bin/activate


# dipendenze
pip install --upgrade pip setuptools wheel
pip install mlx mlx-metal mlx-lm huggingface_hub
pip install --no-build-isolation -e python/


# scarichiamo modello (con VENV attivo)
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('Edge0/Edge0-35B-A3B-preview', local_dir='./models/edge0-35b')"
- questo scaricherà il modello qui "./models/edge0-35b"


# se vuoi cambiare il contesto
edge0/models/edge0-35b/config.json
- riga "max_position_embeddings": 262144
- modificala a: 8192 o 16384 o 32768


# Avvia il Server di Edge0 (Sul terminale apparirà il messaggio: Server running on http://localhost:8080.)
edge0 serve ./models/edge0-35b --port 8080


# testa chiamata
curl http://127.0.0.1:8080/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{
   "model": "edge0-35b",
   "messages": [
     {"role": "user", "content": "Ciao! Dimmi chi sei in una sola frase."}
   ]
 }'
