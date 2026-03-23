# Design of Experiments (DoE)

Data snapshot: 2026-03-17
Repo: PACO
Scope: esperimenti PACO con metriche explainer (impacts/decision/hybrid), tempi post-frontiera, foglie e tipologia scelte.

## 1) Obiettivo
Misurare e confrontare, per ogni istanza BPMN+CPI, il costo e l’esito della costruzione della explained strategy nei tre mode:
1. `impacts_based`
2. `decision_based`
3. `hybrid`

con tracciamento aggiuntivo di:
- numero foglie explainer
- tipologia scelte (`forced`, `arbitrary`, `impacts`, `decision`) per ogni mode
- tempi post-frontiera per fasi del workflow.

## 2) Ipotesi operative
1. `decision_based` deve risultare costruibile quando esiste strategia (status atteso: `success`).
2. `impacts_based` può fallire su casi non separabili.
3. `hybrid` raccoglie sempre la spiegazione costruita (anche se composta da un solo tipo); la composizione si osserva dai conteggi `impacts/decision`.
4. Maggiore complessità BPMN+CPI tende ad aumentare tempi explainer e dimensione explainer.

## 3) Unità sperimentale
Una riga in `experiments` identificata da `(x, y, w)`.

## 4) Fattori e livelli
1. Complessità strutturale: `x`, `y` (con analisi per `x+y`).
2. Variante processo: `z`.
3. Numero impatti: `num_impacts`.
4. Distribuzione scelta: `choice_distribution`.
5. Modalità generazione: `generation_mode`.
6. Intervallo durate: `duration_interval_min/max`.

## 5) Variabili risposta
1. Tempi macro:
   - `time_create_execution_tree`
   - `time_evaluate_cei_execution_tree`
   - `found_strategy_time`
   - `build_strategy_time`
   - `time_explain_strategy`
   - `strategy_tree_time`
2. Tempi per explain mode:
   - `time_explain_strategy_impacts_based`
   - `time_explain_strategy_decision_based`
   - `time_explain_strategy_hybrid`
3. Stati per mode:
   - `explain_strategy_impacts_based_status`
   - `explain_strategy_decision_based_status`
   - `explain_strategy_hybrid_status`
4. Dimensione explainer:
   - `explainer_leaves_impacts_based`
   - `explainer_leaves_decision_based`
   - `explainer_leaves_hybrid`
   - `explainer_leaves_total`
5. Tipologia scelte per mode:
   - `explainer_choices_<mode>_{total,forced,arbitrary,impacts,decision}`

## 5.1) Come viene conteggiata la tipologia delle choice nella strategy
Il conteggio è fatto sulla **strategy tree spiegata** (non sul solo parse tree) e viene calcolato separatamente per ogni mode di spiegazione.

Algoritmo (coerente con l'implementazione in `refinements.py`):
1. Si costruisce la strategy tree del mode corrente (`full_strategy(...)`) usando i BDD del mode (`impacts_based`, `decision_based` o `hybrid`).
2. Si visita la strategy tree con DFS a partire dalla root.
3. Si usa `visited_nodes` (chiave: `StrategyViewPoint.id`) per non contare due volte lo stesso nodo della strategy.
4. Per ogni `choice` presente nel nodo visitato:
   - si prende `bdd = node.explained_choices.get(choice)`
   - se `bdd is None` => la choice è conteggiata come `arbitrary`
   - se `bdd.typeStrategy == FORCED_DECISION` => `forced`
   - se `bdd.typeStrategy == CURRENT_IMPACTS` => `impacts`
   - se `bdd.typeStrategy == DECISION_BASED` => `decision`
5. I conteggi sono deduplicati per `choice.id` (set separati per categoria), quindi la stessa choice non viene ricontata molte volte se riappare in più nodi.
6. `choices_total` è la cardinalità dell'unione dei set:
   - `total = |arbitrary ∪ forced ∪ impacts ∪ decision|`

Metriche salvate per ogni mode:
1. `explainer_choices_<mode>_total`
2. `explainer_choices_<mode>_forced`
3. `explainer_choices_<mode>_arbitrary`
4. `explainer_choices_<mode>_impacts`
5. `explainer_choices_<mode>_decision`

Regole importanti di interpretazione:
1. I conteggi sono **per-mode**: ogni mode ha la sua strategy tree e quindi i suoi conteggi.
2. Se un mode fallisce, i suoi conteggi restano `0`.
3. Se non c'è strategia da spiegare (caso banale), tutti i conteggi restano `0`.
4. Nel mode `hybrid`, il conteggio riflette sempre la strategia ibrida effettivamente costruita; il mix tra `impacts` e `decision` è osservabile tramite i relativi conteggi.

## 6) Procedura sperimentale
1. Avvio benchmark da script utente:
   - `source venv/bin/activate`
   - `./run_benchmark.sh`
2. Pipeline per ogni istanza:
   - creazione execution tree
   - valutazione CEI
   - raffinamento bound
   - ricerca frontiera
   - build strategy
   - explain strategy con tentativi ordinati (`impacts -> decision -> hybrid`)
   - build strategy tree e conteggi finali
3. Persistenza su SQLite (`benchmarks.sqlite`) con migrazione colonne automatica.

## 7) Piano di esecuzione consigliato
Fase A (sanity):
1. Eseguire solo casi piccoli `x+y <= 3`.
2. Verificare cardinalità attesa per bundle piccoli (5400 per combinazione nei dataset correnti).
3. Confermare assenza errori bloccanti e popolamento colonne nuove.

Fase B (scalabilità):
1. Estendere progressivamente `x+y`.
2. Monitorare tempi post-frontiera e tassi di fallimento per mode.
3. Confrontare distribuzioni per `num_impacts`, `generation_mode`, `choice_distribution`.

## 8) Quality gates (accettazione)
1. Nessuna riga con `vte IS NULL` al termine run.
2. Per righe con strategia non banale:
   - `decision_based_status = success` (atteso)
   - `impacts_based_status` coerente con separabilità
   - `hybrid_status` valorizzato e metriche `hybrid` presenti
3. Colonne nuove valorizzate (no NULL sistematici su run nuovi).
4. Notebook risultati eseguibile end-to-end senza output error.

## 9) Rischi / confondenti
1. Modifica involontaria dei bundle `.cpis.gz` altera i dataset di input e rompe comparabilità storica.
2. Notebook con output salvati può introdurre rumore nel diff.
3. Interruzioni manuali (`Ctrl+C`) generano righe incomplete da ripulire.

## 10) Decisione pratica per il prossimo commit
1. Tenere: modifiche `src/**` + (eventualmente) notebook/documentazione risultati.
2. Escludere (se non voluti): `cpi_bundle_x1_y{1,2,3}.cpis.gz` e `current_benchmark.cpi`.
3. Rigenerare `analysis_experiments_explainer.md` se deve riflettere gli ultimi run.
