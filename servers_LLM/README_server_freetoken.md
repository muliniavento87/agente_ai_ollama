Il provider FreeToken fa delle ottimizzazioni e usa il modelo con la quantizzazione NVidia NVFP4.
Il modello che useremo in 8vram e 32gb ram: Qwen3.6-35B-A3B-NVFP4.

- Scarica FreeToken, avvialo e poi scarica il modello "Qwen3.6-35B-A3B-NVFP4"
- Poi chiudi FreeToken e per avviarlo con la configurazione voluta (quantizzazione e grandezza contesto) va lanciato via terminale
- adatta i percorsi in base all'utenza
    C:\Users\banana\.freetoken\models\Qwen3.6-35B-A3B-NVFP4 --host 0.0.0.0 --max-seq-len-override 32768 --max-output-tokens 32768 --num-tokens 32768
