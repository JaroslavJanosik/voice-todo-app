# Voice Todo App

A voice-powered todo application that allows users to manage tasks using voice commands. This project consists of a **Python + Flask** backend and a **SvelteKit** frontend.

---

## 🧩 Project Structure

```
voice-todo-app/
├── backend/         # Flask API for voice processing and task management
├── frontend/
│   ├── svelte/      # SvelteKit app (main frontend)
│   └── html-css-javascript/  # Basic JS/HTML prototype
```

---

## 🖥️ Backend

- Built with **Python 3** and **Flask**
- Accepts voice uploads and manages todo items via REST API
- See [`backend/README.md`](backend/README.md) for setup instructions

### Start Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

---

## 🌐 Frontend (SvelteKit)

- Built with **SvelteKit**, **Vite**, and **TypeScript**
- Provides UI for recording voice and managing tasks
- Communicates with the Flask backend
- See [`frontend/svelte/README.md`](frontend/svelte/README.md) for details

### Start Frontend:
```bash
cd frontend/svelte
npm install
npm run dev
```

---

## 📡 Communication

The frontend sends audio files and task data to the backend via HTTP requests. Ensure the backend is running before starting the frontend.

---

## 📄 License

MIT License
