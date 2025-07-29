# Voice Todo App – Backend

This is the backend service for the **Voice Todo App**, built with **Python** and **Flask**. 
It handles voice processing, task management, and communicates with the frontend via RESTful APIs.

---

## 📦 Prerequisites

- **FFmpeg 4.0+** – required for decoding/encoding audio before it reaches the speech-to-text pipeline. Make sure the `ffmpeg` binary is on your system `PATH`.

  | Platform | One-liner |
  |----------|-----------|
  | **macOS (Homebrew)** | `brew install ffmpeg` |
  | **Ubuntu / Debian** | `sudo apt update && sudo apt install ffmpeg` |
  | **Windows (Chocolatey)** | `winget install ffmpeg` |

```bash
ffmpeg -version   # should print the version banner, not an error
```
---

## 🚀 Features

- Accepts and processes voice recordings **(FFmpeg-powered)**
- Stores todo tasks
- REST API for CRUD operations on todos
- Environment configuration using `.env`

---

## 🧰 Tech Stack

- Python 3.x
- Flask
- SQLite (or your configured DB)
- Werkzeug
- `python-dotenv` for managing environment variables
- **FFmpeg** (system dependency)

---

## 📁 Project Structure

```text
backend/
│
├── app.py             # Entry point
├── config.py          # App configuration
├── routes/            # API route definitions
├── models/            # Database models
├── utils.py           # Helper functions
├── uploads/           # Uploaded voice files
├── instance/          # DB and instance-specific config
├── requirements.txt   # Python dependencies
└── .env               # Environment variables
```

---

## ⚙️ Setup Instructions

0. **Install FFmpeg** (see *Prerequisites* above).
1. **Clone the repo:**
   ```bash
   git clone https://github.com/your-username/voice-todo-app.git
   cd voice-todo-app/backend
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file:**
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   ```
5. **Run the server:**
   ```bash
   flask run
   ```

---

## 📬 API Endpoints

| Method | Endpoint        | Description             |
|--------|------------------|-------------------------|
| POST   | `/upload`        | Upload voice file       |
| GET    | `/tasks`         | Get all tasks           |
| POST   | `/tasks`         | Create a new task       |
| PUT    | `/tasks/<id>`    | Update an existing task |
| DELETE | `/tasks/<id>`    | Delete a task           |

## 📄 License

This project is licensed under the MIT License.
