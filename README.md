# Group Chat Simulator

Proiect de curs: o aplicație web care simulează un grup de chat cu mai mulți useri fictivi ("personas"), fiecare generat de un LLM local (Ollama), cu personalitate și ton propriu.

Vezi [SPEC.md](./SPEC.md) pentru specificația completă (scop, stack, features, out of scope).

Fiecare student implementează acest spec în propriul repo.

## Personas

Toate personas sunt definite într-un singur fișier [`personas.json`](./personas.json), ca listă de obiecte:

```json
{
  "name": "Nea Fănică",
  "personality": "haios, jovial, vorbește în metafore",
  "bio": "Cântăreț de muzică populară",
  "system_prompt": "Joci rolul unui cântăreț de muzică populară. Ești haios, jovial și vorbești în metafore.",
  "temperature": 0.9
}
```

Personas definite momentan în acest repo:

| Nume | Personaj |
|---|---|
| Nea Fănică | Cântăreț de muzică populară — haios, jovial, vorbește în metafore |
| Mircea Eliade | Istoric al religiilor, filozof și scriitor |
| Robi | Un "smecheraș" care vrea să facă și el un ban |

Toate personas folosesc același model Ollama (`gemma3:270m`), apelat cu system prompt-ul propriu — vezi [`ollama_client.py`](./ollama_client.py).

## Stack

Python (FastAPI) + Ollama (model: `gemma3:270m`) + frontend web minimal. Detalii complete în [SPEC.md](./SPEC.md) și planul de implementare pe faze în [PLAN.md](./PLAN.md).
