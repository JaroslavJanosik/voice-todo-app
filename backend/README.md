# Voice Todo App – Backend

This is the backend service for the **Voice Todo App**, built with **Python** and **Flask**. 
It handles voice processing, task management, and communicates with the frontend via RESTful APIs.

---

## 🚀 Features

- Accepts and processes voice recordings
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

---

## 📁 Project Structure

```
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

---

## 🧪 Running Tests

If tests are implemented (e.g., using `pytest`), run them via:

```bash
pytest
```

---

## 📄 License

This project is licensed under the MIT License.
