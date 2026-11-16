Questo provider usa una versione di Qwen 3.6 35b con quantizzazione circa Q3.
Usa un modello interno per ottimizzare il caricamento degli esperti MoE del modello e prendere quelli più usati.
Usa poche risorse perchè fa un parziale streaming da SSD e usa la memoria solo per gli esperti e parte del contesto (con un contesto non esagerato si usano 3 gb di ram/vram).

Segui le istruzioni in "server_edge0_ram_lt_8gb".