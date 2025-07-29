# Voice Todo App – Frontend (Svelte)

This is the Svelte-based frontend for the **Voice Todo App**, a web application that lets users manage their todos using voice commands.

---

## 🎯 Features

- Clean and responsive UI built with SvelteKit
- Connects to the backend Flask API
- Record voice inputs and send them to the backend
- Display and manage todo tasks

---

## 🧰 Tech Stack

- SvelteKit
- TypeScript
- Vite (bundler)
- Fetch API for backend communication

---

## 📁 Project Structure

```
svelte/
├── src/
│   ├── routes/        # Application pages and endpoints
│   ├── components/    # Shared components and utilities
│   ├── styles/        # Global styles
│   └── app.html       # App template
├── package.json       # Project metadata and scripts
├── svelte.config.js   # Svelte configuration
├── vite.config.ts     # Vite bundler configuration
└── tsconfig.json      # TypeScript config
```

---

## ⚙️ Setup Instructions

1. **Navigate to the frontend directory:**
   ```bash
   cd voice-todo-app/frontend/svelte
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Access the app:**
   ```
   http://localhost:5173
   ```

---

## 🔄 Connecting to Backend

By default, the frontend expects the backend Flask server to be running locally. 
If it's running on another host or port, update the API endpoint URL in the appropriate file in `src/`.

---

## 📦 Build for Production

```bash
npm run build
```

---

## 📄 License

This project is licensed under the MIT License.
