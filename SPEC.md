# Group Chat Simulator — Spec Minimal

## Context
Acesta e spec-ul de bază pentru un proiect de curs. Fiecare student își creează propriul repo separat și implementează individual pe baza acestui spec (variații de personas/features sunt binevenite, atâta timp cât rămân în scope).

## Ce e asta
O aplicație web care simulează un grup de chat cu mai mulți useri fictivi, fiecare cu personalitatea lui, generați de un LLM. Userul (tu) poate arunca un mesaj în grup și toți "membrii" reacționează/conversează natural, ca într-un chat real de grup — cu vibe, ton și stil diferite per personaj.

## Scop (pt curs)
Demo simplu, rulabil local, care arată cum poți orchestra mai multe "personas" AI într-o singură conversație coerentă, cu context păstrat între mesaje.

## Stack
- Backend: Python 3 (FastAPI) — expune un endpoint de chat
- LLM: Ollama (model local, ex. llama3) pentru generarea răspunsurilor fiecărui persona
- Frontend: pagină web simplă (HTML/JS minimal) care consumă endpoint-ul FastAPI și afișează chat-ul în timp real
- Stocare conversație: în memorie / JSON local (fără DB)

## Features de bază (in scope)
1. Definire persoane într-un fișier de config (`personas.json`): nume, personalitate/tone, scurt bio.
2. Chat loop în terminal: userul scrie un mesaj, unul sau mai multe personas răspund (pe rând, cu delay simulat de 2-8 minute între răspunsuri, pt vibe de grup chat real).
3. Context/istoric conversație păstrat și trimis la fiecare apel LLM (fiecare persona "vede" ce au zis ceilalți).
4. Output afișat clar în UI (nume + stil vizual per persona).
5. Comandă de reset conversație.

## Out of scope
- Design complex / branding
- Autentificare/useri reali
- Persistență în DB
- Voice/multimedia
- Multi-grup / multi-server (doar un singur grup chat activ)

## Model de date (minim)
```json
{
  "name": "Ana",
  "personality": "sarcastică, mereu în întârziere, iubește memes",
  "bio": "PM la o firmă de gaming"
}
```

## Succes = 
Deschizi pagina web, scrii un mesaj, și 3-4 personas răspund natural (la interval de 2-8 minute), cu personalități distincte, ținând cont de ce au zis ceilalți înainte. Vibe check: dacă pare o conversație reală de grup chat, am reușit.
