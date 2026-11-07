
# 0. Avvia server LLM
cd edge0;
python3.12 -m venv venv;
source venv/bin/activate;
edge0 serve ./models/edge0-35b --port 8080

# 1. Interroga LLM
## Pi Agent
pi --no-session

## cURL
curl http://127.0.0.1:8080/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{
   "model": "edge0-35b",
   "messages": [
     {"role": "user", "content": "Ciao! Dimmi chi sei in una sola frase."}
   ]
 }'


# se vuoi cambiare il contesto
edge0/models/edge0-35b/config.json
- riga "max_position_embeddings": 262144
- modificala a: 8192 o 16384 o 32768