# Plan de implementare — Group Chat Simulator

## Context

Proiectul e la stadiul de spec + fișiere de configurare pentru personas, fără cod de aplicație. Scopul e o aplicație care simulează un grup de chat cu 3-4 personas AI (Ollama local), fiecare cu personalitate proprie, care răspund la mesajele userului cu context păstrat între mesaje. Detalii complete în [SPEC.md](./SPEC.md).

Decizii de arhitectură:
- **Config personas**: un singur model Ollama (`gemma3:270m`), apelat cu system prompt diferit per persona, citit dintr-un `personas.json` (conform modelului din SPEC.md). Renunțăm definitiv la Modelfile-uri per persona.
- **Interfață MVP**: terminal (CLI) întâi — felia verticală e un chat loop funcțional în terminal, care lovește Ollama real. Web UI vine peste același backend, într-o fază ulterioară.
- **Delay simulat**: configurabil printr-un env var, cu valori mici (secunde) în dev și 2-8 minute în demo/producție.

Fazele sunt gândite ca să avem, imediat după Faza 2, o felie verticală completă și rulabilă: user scrie un mesaj în terminal → o persona reală (via Ollama) răspunde cu personalitate proprie, cu istoric păstrat. Fazele următoare adaugă lățime (mai multe personas, delay, web) peste acest schelet funcțional.

## Fazele

### Faza 1 — Fundație: config personas + client Ollama
- Curăță repo: commit pentru ștergerea `Modelfile.personaj1-3` și `personaj1-3.md`; elimină mențiunile aferente din README.md.
- `personas.json` la rădăcină, cu 3 personas (nume, personality, bio) — traduce cele 3 personaje existente (cântăreț de muzică populară, Mircea Eliade, "smecheraș") în noul format.
- `requirements.txt` (fastapi, uvicorn, httpx sau `ollama` python client, python-dotenv opțional).
- `ollama_client.py`: funcție `generate_response(system_prompt, temperature, history) -> str` care apelează Ollama local (`http://localhost:11434/api/chat` sau lib `ollama`) cu `gemma3:270m`.
- Verificare: un script/REPL ad-hoc care apelează `generate_response` cu un system prompt hardcodat și printează răspunsul — confirmă că Ollama local + modelul răspund.

### Faza 2 — FELIE VERTICALĂ: chat loop CLI, 1 persona
- `conversation.py`: model simplu de istoric în memorie (listă de mesaje `{role, name, content}`), funcții `add_message`, `get_history`, `reset`.
- `main.py`: loop CLI — userul scrie un mesaj în terminal, mesajul intră în istoric, un singur persona (primul din `personas.json`) generează un răspuns real via `ollama_client`, răspunsul e afișat cu numele personajului.
- **La finalul acestei faze**: `python main.py` → scrii un mesaj → primești un răspuns real, generat de LLM, cu personalitatea persoanei respective. End-to-end funcțional, gata de demo minimal.

### Faza 3 — Multi-persona, delay simulat, context complet, reset
- Extinde loop-ul CLI: toate cele 3 (sau N) personas din `personas.json` răspund pe rând la fiecare mesaj al userului; fiecare persona vede în context și răspunsurile date deja de ceilalți în aceeași rundă.
- Delay simulat între răspunsuri, controlat printr-un env var (ex. `RESPONSE_DELAY_MIN_S` / `RESPONSE_DELAY_MAX_S`), cu default mic pentru dev.
- Comandă `/reset` în CLI care golește istoricul conversației.

### Faza 4 — Backend FastAPI peste aceeași logică
- Extrage logica de business (istoric, orchestrare personas, apel Ollama) în module reutilizabile, independente de CLI — deja separate din Fazele 2-3 dacă structura e păstrată curată.
- `app.py` (FastAPI): `POST /chat` (primește mesaj user, declanșează generarea răspunsurilor personas cu delay, în background/async), `GET /messages` sau SSE pentru a livra răspunsurile pe măsură ce apar, `POST /reset`.
- Verificare: `curl`/httpie către endpointurile FastAPI confirmă același comportament ca CLI-ul, dar prin HTTP.

### Faza 5 — Frontend web minimal
- Pagină HTML/JS simplă (fără framework) care: trimite mesajul userului la `POST /chat`, face polling sau ascultă SSE pe `/messages`, afișează mesajele cu nume + stil vizual distinct per persona, are un buton de reset.
- Verificare manuală în browser: deschizi pagina, scrii un mesaj, vezi personas răspunzând unul câte unul.

### Faza 6 — Polish & demo readiness
- Setează delay-ul implicit la 2-8 minute pentru modul demo (păstrând override rapid pentru dev).
- Stilizare minimă (culoare/etichetă per persona) în frontend.
- Actualizează README.md cu instrucțiuni de rulare (Ollama trebuie pornit + modelul `gemma3:270m` pull-uit, `uvicorn app:app`, deschide pagina).
- "Vibe check" end-to-end: succesul definit în SPEC.md — mesaj user + 3-4 personas răspund natural, ținând cont de conversație.

## Fișiere critice

- `personas.json` — sursa unică de adevăr pentru personas (nou)
- `ollama_client.py` — singurul loc care vorbește cu Ollama (nou)
- `conversation.py` — istoric conversație în memorie (nou)
- `main.py` — CLI, felia verticală din Faza 2 (nou)
- `app.py` — FastAPI, Faza 4 (nou)
- `static/index.html` (sau echivalent) — frontend Faza 5 (nou)
- `README.md`, `SPEC.md` — de actualizat la Faza 1 (README) și Faza 6 (README)
- `Modelfile.personaj1-3`, `personaj1-3.md` — de șters/commituit definitiv la Faza 1

## Verificare

- Faza 1: rulare manuală a clientului Ollama cu un prompt de test → răspuns valid.
- Faza 2 (felie verticală): `python main.py`, trimite un mesaj, confirmă răspuns coerent cu personalitatea personajului.
- Faza 3: aceeași rulare, confirmă că toate personas răspund, cu delay vizibil (redus în dev) și că răspunsurile ulterioare țin cont de cele anterioare; testează `/reset`.
- Faza 4: `curl -X POST localhost:8000/chat -d '{"message": "..."}'` + verifică `/messages`.
- Faza 5-6: test manual în browser, urmărind "vibe check"-ul din SPEC.md.
