# Per ottimi risultati [testato con Qwen3.6-35B-A3B-Q4]
1. Analisi richiesta e creazione documenti (funzionale e tecnico)
```bash
# avvia Pi
pi --no-session
# usa la skill (recupero requisiti con intervista)
/skill:grill-with-docs  In questa fase non implementare nulla, voglio solo dei documenti tecnici. RICHIESTA_UTENTE
# attendi e copia le domande, rispondi sotto le domande e reinvia tutto al modello

# attendi e quando ha finito avrai i documenti per passare all'implementazione
```
2. Implementazione a partire dai documenti creati
    - inseriamo i documenti prodotti nella cartella "p/fase_0" (precedentemente vuota)
    - avviamo l'elaborazione che scompone i dettagli tecnici in microtask e li implementa (facendo commit su git), tutto nella cartella "output/"
```bash
cd p; python3 workflow_auto.py
```

```Markdown
Voglio creare una app su html statico che stampa una parola "ciao" e un tasto sotto che cambia la parola stampata con il timestamp attuale. Voglio che sia graficamente gradevole
```