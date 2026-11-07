# Workflow
/skill:grill-with-docs
    analisi con creazione documenti

/skill:to-spec
    crea specifica formale dai documenti creati prima
        es. "/skill:to-spec Crea il documento di specifiche tecniche basato sulla nostra sessione di grill-with-docs che ha creato i documenti dentro "test/"."
/skill:to-tickets
    (SOLO PER TASK COMPLESSI) Se l'intervento è ampio e richiede più sessioni, questa skill suddivide la specifica in ticket o tracer bullets atomici, ordinati in base alle dipendenze (blocchi)

/skill:implement-spec
    Su tutto se hai usato "/skill:to-spec", altrimenti usala su singolo ticket se hai usato "/skill:to-tickets"

/skill:code-review
    Revisione rigorosa del codice scritto