# Group Chat Simulator

Proiect de curs: o aplicație web care simulează un grup de chat cu mai mulți useri fictivi ("personas"), fiecare generat de un LLM local (Ollama), cu personalitate și ton propriu.

Vezi [SPEC.md](./SPEC.md) pentru specificația completă (scop, stack, features, out of scope).

Fiecare student implementează acest spec în propriul repo.

## Personas

Fiecare persona e definit într-un fișier `.md` cu două câmpuri:

```
temperature: 0.90
system prompt: <descrierea personajului / cum trebuie să joace rolul>
```

Personas definite momentan în acest repo:

| Fișier | Personaj |
|---|---|
| `personaj1.md` | Cântăreț de muzică populară — haios, jovial, vorbește în metafore |
| `personaj2.md` | Mircea Eliade |
| `personaj3.md` | Un "smecheraș" care vrea să facă și el un ban |

> Notă: `personaj1 copy.md` e un fișier placeholder (lorem ipsum), momentan neterminat.

## Stack

Python (FastAPI) + Ollama + frontend web minimal. Detalii complete în [SPEC.md](./SPEC.md).
