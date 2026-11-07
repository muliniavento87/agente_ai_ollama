# Per pullare un modello e settare una configurazione custom per lui
- disponibili (agentici):
```bash
# LFM 2.5 24b (contesto 32k)
ollama create lfm2.5-32k -f lfm2.5-32k
# Ornith 1.5 IQ3 9b (contesto 8k)
ollama create Ornith-1.5-9b-IQ3-M-8k -f Ornith-1.5-9b-IQ3-M-8k
# Ornith 1.5 Q4 9b (contesto 32k)
ollama create Ornith-1.5-9b-Q4-K-M-32k -f Ornith-1.5-9b-Q4-K-M-32k
# Qwen 3.6 Q4 35b A3B (MoE) (contesto 32k)
ollama create Qwen3.6-35B-A3B-Q4-K-M-32k -f Qwen3.6-35B-A3B-Q4-K-M-32k
# Saluki 27b IQ2 (contesto 32k) [derivato da Qwen 3.8 27b con quantizzazione particolare, buono ma un pò lento]
ollama create Saluki-27b-IQ2-32k -f Saluki-27b-IQ2-32k
```