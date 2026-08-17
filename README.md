# Group Chat Simulator

Proiect de curs: o aplicație web care simulează un grup de chat cu mai mulți useri fictivi ("personas"), fiecare generat de un LLM local (Ollama), cu personalitate și ton propriu.

Vezi [SPEC.md](./SPEC.md) pentru specificația completă (scop, stack, features, out of scope).

Fiecare student implementează acest spec în propriul repo.

## Personas

Toate personas sunt definite într-un singur fișier [`personas.json`](./personas.json), ca listă de obiecte:

```json
{
  "id": "cantaret",
  "name": "Cântărețul",
  "personality": "haios, jovial, vorbește în metafore",
  "bio": "Cântăreț de muzică populară",
  "system_prompt": "Joci rolul unui cântăreț de muzică populară. Ești haios, jovial și vorbești în metafore.",
  "temperature": 0.7,
  "emoji": "🪗"
}
```

`id` e un identificator stabil bazat pe rol (nu pe numele personajului), gândit să rămână neschimbat chiar dacă `name` se schimbă.

Personas definite momentan în acest repo:

| Nume | Personaj |
|---|---|
| Cântărețul | Cântăreț de muzică populară — haios, jovial, vorbește în metafore |
| Mircea Eliade | Istoric al religiilor, filozof și scriitor |
| Șmecherașul | Un "smecheraș" care vrea să facă și el un ban |
| Bunica Ileana | Bunică de la țară — grijulie, glumeață, mereu îngrijorată dacă ai mâncat |
| Vecina Maria | Vecina bârfitoare — știe tot ce se-ntâmplă în bloc |
| Gigi Taximetristul | Taximetrist filozof — morocănos la suprafață, are o părere despre orice |
| Mia Influencerița | Influenceriță pe social media — entuziastă, presară cuvinte în engleză |
| Nelu Ardeleanul | Ardelean liniștit și tacticos — nu se grăbește niciodată |
| Profesorul Ionescu | Profesor de matematică la pensie — pedant, corectează pe toată lumea |

Toate personas folosesc același model Ollama (`gemma4:e2b`), apelat cu system prompt-ul propriu — vezi [`ollama_client.py`](./ollama_client.py).

## Stack

Python (FastAPI) + Ollama (model: `gemma4:e2b`) + frontend web minimal. Detalii complete în [SPEC.md](./SPEC.md) și planul de implementare pe faze în [PLAN.md](./PLAN.md).

## Cum rulezi

1. **Ollama** trebuie să ruleze local, cu modelul deja descărcat:
   ```bash
   ollama pull gemma4:e2b
   ```
2. **Dependențe Python** (necesită Python 3.9+):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Teste** (suita pytest, scrisă TDD — vezi [PLAN.md](./PLAN.md)):
   ```bash
   pytest
   ```
4. **Chat în terminal** (CLI):
   ```bash
   python3 main.py
   ```
5. **Chat în browser** (backend FastAPI + frontend static):
   ```bash
   uvicorn app:app --reload --port 8000
   ```
   Deschide [http://localhost:8000](http://localhost:8000).

   Fiecare conversație e persistată separat (câte un fișier JSON în `conversations/`, ignorat în git). Din UI poți schimba conversația activă din dropdown-ul de sus sau porni una nouă cu „+ Nouă" — vezi Faza 8 din [PLAN.md](./PLAN.md) pentru detalii.

### Mod demo vs. dezvoltare

Implicit, delay-ul simulat între răspunsurile personas e foarte scurt (0.5-1.5 secunde), ca să nu aștepți la fiecare test. Pentru demo-ul "adevărat" (2-8 minute între răspunsuri, conform [SPEC.md](./SPEC.md)):

```bash
cp .env.example .env
# apoi decomentează RESPONSE_DELAY_MIN_S / RESPONSE_DELAY_MAX_S în .env
```
