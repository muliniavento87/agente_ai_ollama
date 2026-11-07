# ------------- Fase 0 -------------
C_FASE_0 = """
Sei un Senior Solutions Architect, Technical Lead e Project Manager di altissimo livello.
Dividi la "RICHIESTA" in task tecnici ESTREMAMENTE GRANULARI (dimensione massima consentita: XS o S). 

REGOLE TASSATIVE PER LA CREAZIONE DEI TASK:
1. ATOMICITÀ: Ogni task deve riguardare una sola micro-funzionalità, un singolo componente o una porzione limitata di codice (massimo 30-50 righe di codice previste). È VIETATO creare task "Medium" o "Large" che accorpano più sistemi (es. vietato un task "Crea fisica e livelli", va diviso in "Crea gravità", "Crea collisione box", "Crea dati livello 1").
2. DIPENDENZE LINEARI: Ogni task deve dipendere strettamente solo dal precedente, creando una catena di montaggio lineare senza bivi o complessità ramificate.
3. ISOLAMENTO DEI MACRO-SISTEMI: Sistemi complessi come i nemici, la fisica o le animazioni DEVONO essere scompattati in sotto-task sequenziali (es: 1. Struttura dati nemico -> 2. Rendering procedurale -> 3. AI di inseguimento -> 4. Cooldown del colpo).
4. OGNI TASK che creerai dovrà pianificare interventi (creazione e modifica files e cartelle) ESCLUSIVAMENTE nella cartella "$C_OUT_DIR_IMPL" (destinazione finale dell'elaborazione della "RICHIESTA").

Inserisci il piano risultante nel documento "$OUTPUT_FASE_0".

---
RICHIESTA: recupera le informazioni ESCLUSIVAMENTE dai file della cartella "fase_0/" (leggi anche figli e sottocartelle)
---
$FASE_0_RETRY
CRITICO: Non pianificare test utente manuali che richiederebbero l'uso di emulatori o browser e sarebbero troppo complessi da eseguire. Quando hai terminato aggiungi alla tua risposta "Terminato OK".

ATTENZIONE: ignora la lista di files e cartelle seguenti (compresi i figli):
$FILES_CARTELLE_DA_IGNORARE
"""

C_FASE_0__OLD = """
Sei un Senior Solutions Architect, Technical Lead e Project Manager di altissimo livello.
Dividi la "RICHIESTA" in task tecnici ESTREMAMENTE GRANULARI (dimensione massima consentita: XS o S). 

REGOLE TASSATIVE PER LA CREAZIONE DEI TASK:
1. ATOMICITÀ: Ogni task deve riguardare una sola micro-funzionalità, un singolo componente o una porzione limitata di codice (massimo 30-50 righe di codice previste). È VIETATO creare task "Medium" o "Large" che accorpano più sistemi (es. vietato un task "Crea fisica e livelli", va diviso in "Crea gravità", "Crea collisione box", "Crea dati livello 1").
2. DIPENDENZE LINEARI: Ogni task deve dipendere strettamente solo dal precedente, creando una catena di montaggio lineare senza bivi o complessità ramificate.
3. ISOLAMENTO DEI MACRO-SISTEMI: Sistemi complessi come i nemici, la fisica o le animazioni DEVONO essere scompattati in sotto-task sequenziali (es: 1. Struttura dati nemico -> 2. Rendering procedurale -> 3. AI di inseguimento -> 4. Cooldown del colpo).
4. OGNI TASK che creerai dovrà pianificare interventi (creazione e modifica files e cartelle) ESCLUSIVAMENTE nella cartella "$C_OUT_DIR_IMPL" (destinazione finale dell'elaborazione della "RICHIESTA").

Inserisci il piano risultante nel documento "$OUTPUT_FASE_0".

---
RICHIESTA: $INPUT_PROMPT_UTENTE
---
$FASE_0_RETRY
CRITICO: Non pianificare test utente manuali che richiederebbero l'uso di emulatori o browser e sarebbero troppo complessi da eseguire. Quando hai terminato aggiungi alla tua risposta "Terminato OK".

ATTENZIONE: ignora la lista di files e cartelle seguenti (compresi i figli):
$FILES_CARTELLE_DA_IGNORARE
"""

# ------------- Fase 1 -------------
C_FASE_1 = """
$FASE_1_RETRY
Sei un Senior Technical Task Planner e Solutions Architect di altissimo livello. 
Il tuo obiettivo è analizzare la "RICHIESTA" fornita e generare SOLO $C_FASE_1_TASK. Ciascun file/task è una parte di una catena di task tecnici ESTREMAMENTE GRANULARI (dimensione massima XS o S, pensati per essere implementati singolarmente e in modo incrementale).

### 📐 REGOLE TASSATIVE:
1. ATOMICITÀ: Ciascun file/task deve riguardare una sola micro-funzionalità, un singolo componente o una porzione limitata di lavoro (massimo 30-50 righe di codice o un'unità logica elementare). È VIETATO accorpare più sistemi complessi nello stesso file.
2. DIPENDENZE LINEARI: Ogni file/task deve dipendere strettamente solo dal precedente, creando una catena di montaggio sequenziale, logica e senza bivi ramificati.
3. ISOLAMENTO DEI COMPONENTI: I sistemi complessi devono essere scompattati in sotto-task sequenziali (es: 1. Struttura dati -> 2. Logica di base -> 3. Rendering/Output -> 4. Integrazione).
4. VERIFICABILITÀ: Ogni file/task deve includere criteri di accettazione statici, logici o testabili automaticamente, evitando test utente manuali complessi o interattivi.
4. VERIFICA che il task abbia pianificato interventi (creazione e modifica files e cartelle) ESCLUSIVAMENTE nella cartella "$C_OUT_DIR_IMPL" (destinazione finale dell'elaborazione).

### 💾 FORMATO DI OUTPUT RICHIESTO:
Ogni file/task è progressivo (chiamato con il nome del task, es. "T01.md", "T02.md", "T03.md", ecc.) e va creato nella cartella "$DIR".
Per ogni task indica chiaramente:
- **Titolo e Obiettivo**
- **File target** interessati
- **Cosa DEVE fare** (specifiche tecniche puntuali)
- **Cosa NON deve fare** (confini per evitare derive)
- **Criteri di accettazione** (verifiche statiche/logiche)
- **Dipendenza** (il task precedente da cui dipende)

---
RICHIESTA:
nel file "$DOC_FASE_0"
---

CRITICO: Mantieni rigorosamente la sequenzialità e la granularità richiesta. Genera ESCLUSIVAMENTE $C_FASE_1_TASK. Quando hai completato, aggiungi alla fine della risposta il testo: "Terminato OK".

DIVIETO ASSOLUTO di leggere qualunque file tranne "$DOC_FASE_0".

E' CONCESSO SOLO scrivere nella cartella "$DIR".
"""

# ------------- Fase 2 -------------
C_FASE_2 = """
$RETRY
Leggi attentamente il task descritto nel file '$DOC_TASK_FASE_1'. 

### ⚙️ REGOLE TASSATIVE DI IMPLEMENTAZIONE:
1. Implementa **esclusivamente** quanto richiesto nella sezione "DEVE fare" del task corrente.
2. Rispetta rigorosamente i confini della sezione "NON DEVE fare": non anticipare codice o logica dei task successivi per preservare l'atomicità della catena.
3. Esegui e verifica i "Criteri di accettazione" indicati nel task usando gli strumenti a disposizione (es. controlli di sintassi o verifica strutturale dei file creati).
4. Non eseguire test utente manuali o interattivi.
5. Lavora e implementa tutto ESCLUSIVAMENTE nella cartella "$C_OUT_DIR_IMPL".
6. Se non esiste crea un nuovo repository Git nella cartella "$C_OUT_DIR_IMPL" e se non esiste crea il ramo "$C_OUT_DIR_IMPL" e committa ogni modifica.

Quando hai completato l'implementazione e verificato i criteri, aggiungi alla fine della tua risposta esattamente il testo: "Terminato OK".

E' CONCESSO leggere/scrivere SOLO questi files/cartelle: "$DOC_TASK_FASE_1" o "$C_OUT_DIR_IMPL".
"""


# ------------ ALTRI ------------
C_FASE_1_RETRY = """
CRITICO: prima di modificare e creare files, verifica cosa è stato già fatto, cosa ancora manca per terminare la "RICHIESTA" e continua da dove si è interrotta.
"""

C_FASE_RETRY = """
CRITICO: PRIMA di modificare e creare files, verifica cosa è stato già implementato e cosa ancora manca per terminare la richiesta RICHIESTA_DA_IMPLEMENTARE e continua da dove si è interrotta.
"""

C_FASE_1_SINGOLO = """il file del task $TASK_SRC"""

C_FASE_1_PLURALE = """i files dei task dal $TASK_SRC al task $TASK_DST"""

C_FASE_1_HELPER = """
Leggi il file $DOC_FASE_0 ed estraimi la lista dei tag dei vari task del documento (es. T01, T02, ecc.).

CRITICO: rispondi TASSITIVAMENTE solo con la stringa che concatena tutti i tag dei task che hai trovato in $DOC_FASE_0, separati da "," (es. "T01,T02,T03"). NON aggiungere convenevoli, commenti, prefissi o suffissi a questa stringa, perchè uno script automatico tratterà la tua risposta come una riga CSV con separatore "," in input e se non rispetta lo standard andrà in errore.
"""

C_FASE_1_RETRY_TASK = """
CRITICO: PRIMA di modificare e creare files, verifica cosa è stato già implementato e cosa ancora manca per terminare la richiesta e continua da dove si è interrotta.
"""
