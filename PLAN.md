# Plan de implementare — Group Chat Simulator

## Context

Proiectul e la stadiul de spec + fișiere de configurare pentru personas, fără cod de aplicație. Scopul e o aplicație care simulează un grup de chat cu 3-4 personas AI (Ollama local), fiecare cu personalitate proprie, care răspund la mesajele userului cu context păstrat între mesaje. Detalii complete în [SPEC.md](./SPEC.md).

Decizii de arhitectură:
- **Config personas**: un singur model Ollama (`gemma4:e2b`), apelat cu system prompt diferit per persona, citit dintr-un `personas.json` (conform modelului din SPEC.md). Renunțăm definitiv la Modelfile-uri per persona.
- **Interfață MVP**: terminal (CLI) întâi — felia verticală e un chat loop funcțional în terminal, care lovește Ollama real. Web UI vine peste același backend, într-o fază ulterioară.
- **Delay simulat**: configurabil printr-un env var, cu valori mici (secunde) în dev și 2-8 minute în demo/producție.

Fazele sunt gândite ca să avem, imediat după Faza 2, o felie verticală completă și rulabilă: user scrie un mesaj în terminal → o persona reală (via Ollama) răspunde cu personalitate proprie, cu istoric păstrat. Fazele următoare adaugă lățime (mai multe personas, delay, web) peste acest schelet funcțional.

## Metodologie: Test-Driven Development

Din Faza 2 încolo, componentele cu logică deterministă se scriu TDD (roșu → verde → refactor): întâi testul în `tests/test_*.py`, apoi implementarea minimă care îl trece.

- **Testabil cu TDD**: `conversation.py` (istoric, reset), orchestrarea multi-persona din Faza 3, parsing/validare `personas.json`, endpointurile FastAPI din Faza 4 (cu `TestClient`). Apelurile către Ollama (`ollama_client.generate_response`) sunt mockuite în aceste teste, ca să ruleze rapid și fără dependență de un model local pornit.
- **Nu e testabil unitar** (rămâne verificare manuală/smoke, ca în secțiunea Verificare de mai jos): răspunsul efectiv generat de `gemma4:e2b` — e non-determinist, deci nu are sens un assert pe conținut; doar confirmăm că apelul reușește și întoarce text.
- Framework: `pytest`, rulat cu `pytest` din rădăcina proiectului. Testele stau în `tests/`, oglindind modulele (`tests/test_conversation.py`, `tests/test_app.py` etc.).

## Fazele

### Faza 1 — Fundație: config personas + client Ollama
- Curăță repo: commit pentru ștergerea `Modelfile.personaj1-3` și `personaj1-3.md`; elimină mențiunile aferente din README.md.
- `personas.json` la rădăcină, cu 3 personas (nume, personality, bio) — traduce cele 3 personaje existente (cântăreț de muzică populară, Mircea Eliade, "smecheraș") în noul format.
- `requirements.txt` (fastapi, uvicorn, httpx sau `ollama` python client, python-dotenv opțional).
- `ollama_client.py`: funcție `generate_response(system_prompt, temperature, history) -> str` care apelează Ollama local (`http://localhost:11434/api/chat` sau lib `ollama`) cu `gemma4:e2b`.
- Verificare: un script/REPL ad-hoc care apelează `generate_response` cu un system prompt hardcodat și printează răspunsul — confirmă că Ollama local + modelul răspund.

### Faza 2 — FELIE VERTICALĂ: chat loop CLI, 1 persona
- `tests/test_conversation.py` întâi: teste pentru `add_message`, `get_history`, `reset` — apoi `conversation.py` (model simplu de istoric în memorie, listă de mesaje `{role, name, content}`) ca să treacă testele.
- `main.py`: loop CLI — userul scrie un mesaj în terminal, mesajul intră în istoric, un singur persona (primul din `personas.json`) generează un răspuns real via `ollama_client`, răspunsul e afișat cu numele personajului. (Nu e TDD — e loop-ul de I/O care leagă piesele, verificat manual.)
- **La finalul acestei faze**: `python main.py` → scrii un mesaj → primești un răspuns real, generat de LLM, cu personalitatea persoanei respective. End-to-end funcțional, gata de demo minimal.

### Faza 3 — Multi-persona, delay simulat, context complet, reset
- `tests/test_orchestrator.py` (nu `test_conversation.py` — acela testează doar clasa `Conversation` de bază) cu teste pentru orchestrarea multi-persona (toate personas răspund pe rând, fiecare vede răspunsurile anterioare din rundă) și pentru reset — cu `ollama_client.generate_response` mockuit — apoi implementarea în `orchestrator.py`/`main.py`.
- Delay simulat între răspunsuri, controlat printr-un env var (ex. `RESPONSE_DELAY_MIN_S` / `RESPONSE_DELAY_MAX_S`), cu default mic pentru dev. (Testat doar că parametrii sunt citiți corect, nu că timpul efectiv trece.)
- Comandă `/reset` în CLI care golește istoricul conversației.

### Faza 4 — Backend FastAPI peste aceeași logică
- Extrage logica de business (istoric, orchestrare personas, apel Ollama) în module reutilizabile, independente de CLI — deja separate din Fazele 2-3 dacă structura e păstrată curată.
- `tests/test_app.py` întâi, cu `fastapi.testclient.TestClient` și `generate_response` mockuit: teste pentru `POST /chat`, `GET /messages`, `POST /reset` — apoi `app.py` (FastAPI) ca să treacă testele. (Aceste rute au fost înlocuite ulterior de rutele per-conversație din Faza 8 — `/conversations/{id}/...` — vezi mai jos.)
- Verificare manuală suplimentară: `curl`/httpie către endpointurile FastAPI confirmă același comportament ca CLI-ul, dar prin HTTP.

### Faza 5 — Frontend web minimal
- Pagină HTML/JS simplă (fără framework) care: trimite mesajul userului la `POST /chat`, face polling sau ascultă SSE pe `/messages`, afișează mesajele cu nume + stil vizual distinct per persona, are un buton de reset.
- Verificare manuală în browser: deschizi pagina, scrii un mesaj, vezi personas răspunzând unul câte unul.
- Autocompletare `@nume` la scriere (dropdown filtrat, navigabil cu tastatura), listă vizibilă cu toate personas sub titlu, și indicator „X scrie..." (puncte animate) cât timp o persona generează efectiv un răspuns — `app.py` expune `GET /conversations/{id}/typing` (`{"name": ...}`), actualizat din `generate_round`; frontend-ul face polling pe el la fiecare 1.5s, alături de `/messages`.

### Faza 6 — Polish & demo readiness
- Setează delay-ul implicit la 2-8 minute pentru modul demo (păstrând override rapid pentru dev).
- Stilizare minimă (culoare/etichetă per persona) în frontend.
- Actualizează README.md cu instrucțiuni de rulare (Ollama trebuie pornit + modelul `gemma4:e2b` pull-uit, `uvicorn app:app`, deschide pagina).
- "Vibe check" end-to-end: succesul definit în SPEC.md — mesaj user + 3-4 personas răspund natural, ținând cont de conversație.

### Faza 7 — Orchestrare inteligentă (post-MVP)
Orchestrarea din Fazele 3-6 era inițial provizorie: round-robin, toate personas răspund pe rând la fiecare mesaj, filtrate doar de mențiuni `@nume` (vezi `mentions.py`). Nu ținea cont de relevanță — într-un grup chat real, nu toată lumea reacționează la fiecare mesaj.

**Decis și implementat**: selecție probabilistă pe mențiuni active, în `responders.py` (`pending_mentions` + `response_probabilities` + `select_responders`). Operează pe tot istoricul conversației, nu doar pe ultimul mesaj.
- O mențiune `@nume` rămâne "activă" (pending) pentru o persona de la momentul în care a fost menționată până când acea persona vorbește din nou — indiferent câte mesaje trec între timp. Mențiunea poate veni de la user SAU de la altă persona (personas se pot menționa între ele, nu doar userul le poate menționa).
- Când există cel puțin o persona cu mențiune activă: grupul menționat își împarte în total 80% probabilitate de răspuns (`MENTIONED_SHARE`), egal între membri; grupul fără mențiune activă își împarte restul de 20% (`UNMENTIONED_SHARE`), egal între membri. Fiecare persona decide independent (Bernoulli) — pot răspunde 0, una, mai multe sau toate.
  - Ex. 3 personas, 2 cu mențiune activă: 40% / 40% / 20%. 3 personas, 1 cu mențiune activă: 80% / 10% / 10%.
  - Caz de margine — toate personas au mențiune activă (grup fără mențiune gol): grupul menționat primește 100%, împărțit egal.
  - Caz de margine — ultimul mesaj conține o mențiune care nu se potrivește nicio persona, și nimeni altcineva n-are mențiune activă: nimeni nu răspunde.
- Fără nicio mențiune activă (nici curentă, nici mai veche, nerăspunsă încă): cade pe euristica de relevanță din `routing.py` (deterministă, neschimbată), aplicată pe ultimul mesaj.
- `select_responders(history, personas, rng=random.random)` — ia acum istoricul complet (`Conversation.get_history()`), nu doar textul ultimului mesaj; `rng` e injectabil pentru teste deterministe (vezi `tests/test_responders.py`), la fel `create_app(..., rng=...)` în `app.py`.
- `orchestrator.py` (`BEHAVIOR_GUIDELINES`) instruiește explicit (directiv, nu opțional) personas să folosească `@Nume` când se adresează direct altcuiva din chat (user sau altă persona), cu exemple curente (`@Cântărețul`, `@Eliade`) — verificat cu Ollama real că funcționează repetat, inclusiv o persona menționând trei altele într-un singur răspuns.
- Dacă toate tragerile Bernoulli dintr-o rundă cu mențiuni active pică pe "nu" (nimeni nu răspunde), `select_responders` garantează totuși un răspuns — alege persoana cu cea mai mare probabilitate din acea rundă. (Cazul "mențiune explicită ce nu se potrivește nicio persona" rămâne "nu răspunde nimeni", neschimbat.)

Idei rămase de explorat, fără decizie fermă încă:
- Personas care nu au vorbit de un timp să aibă șansă mai mică să sară în conversație fără motiv (independent de mențiuni).
- Extinderea euristicii de relevanță (fără mențiuni active) cu o pondere probabilistă similară, în loc de all-or-nothing.

### Faza 8 — Persistență conversații (JSON per conversație) — IMPLEMENTAT
Istoricul trăia doar în memorie (`Conversation`) — un restart de server sau proces CLI îl pierdea definitiv. Acum fiecare conversație e persistată într-un fișier JSON propriu, în directorul `conversations/` (ignorat în git), numit după un id (uuid4 hex), cu `created_at` separat pentru sortare.
- `conversation_store.py` — `ConversationStore`: `create`/`list_conversations`/`load_messages`/`append_message`/`reset`/`exists`, testat TDD în `tests/test_conversation_store.py` (director temporar `tmp_path`).
- `app.py` expune multi-conversație: `GET /conversations` (listă, cu titlu derivat din primul mesaj + `message_count`), `POST /conversations` (creează una nouă), `GET/POST /conversations/{id}/messages|chat|reset`. La pornire, dacă nu există nicio conversație pe disc, se creează una implicit.
- Frontend (`static/index.html`): dropdown cu toate conversațiile + buton „+ Nouă"; id-ul conversației active e ținut în `localStorage` (`gcs_conversation_id`), ca la refresh să rămâi pe aceeași conversație.
- Rămâne un singur grup chat activ per conversație (CLI-ul din `main.py` nu a fost conectat la persistență — rămâne efemer, în memorie, neschimbat).

## Fișiere critice

- `personas.json` — sursa unică de adevăr pentru personas (nou)
- `personas_store.py` — încarcă/parsează `personas.json` (nou)
- `config.py` — citește configurare din environment (`.env`): model, delay, nume user (nou)
- `ollama_client.py` — singurul loc care vorbește cu Ollama (nou)
- `conversation.py` — istoric conversație în memorie (nou)
- `mentions.py` / `routing.py` / `responders.py` — decid cine răspunde: mențiuni explicite `@nume`, cu prioritate, altfel euristică de relevanță (Faza 7, nou)
- `main.py` — CLI, felia verticală din Faza 2 (nou)
- `app.py` — FastAPI, Faza 4 (nou)
- `static/index.html` (sau echivalent) — frontend Faza 5 (nou)
- `README.md`, `SPEC.md` — de actualizat la Faza 1 (README) și Faza 6 (README)
- `Modelfile.personaj1-3`, `personaj1-3.md` — de șters/commituit definitiv la Faza 1
- `tests/` — suita pytest, crescută TDD din Faza 2 încolo (nou)
- `conversation_store.py` — persistență JSON per conversație, Faza 8 (nou)
- `conversations/` — director cu câte un fișier JSON per conversație, Faza 8 (nou, de adăugat în `.gitignore`)

## Verificare

- Faza 1: rulare manuală a clientului Ollama cu un prompt de test → răspuns valid.
- Faza 2 (felie verticală): `pytest` verde pentru `conversation.py`; manual, `python main.py`, trimite un mesaj, confirmă răspuns coerent cu personalitatea personajului.
- Faza 3: `pytest` verde pentru orchestrare multi-persona + reset (mockuit); manual, confirmă că toate personas răspund, cu delay vizibil (redus în dev) și că răspunsurile ulterioare țin cont de cele anterioare.
- Faza 4: `pytest` verde pentru `app.py` (`TestClient`, mockuit); manual, `curl -X POST localhost:8000/chat -d '{"message": "..."}'` + verifică `/messages`.
- Faza 5-6: test manual în browser, urmărind "vibe check"-ul din SPEC.md.
