// Select elements
const recordBtn = document.getElementById('record-btn');
const taskList = document.getElementById('task-list');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// 🎤 Toggle Recording
recordBtn.addEventListener('click', async () => {
    if (isRecording) {
        mediaRecorder.stop();
    } else {
        try {
            audioChunks = [];
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('file', audioBlob, 'recording.wav');

                const response = await fetch('http://127.0.0.1:5000/upload', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();
                if (data.transcription) {
                    addTask(data.transcription);
                }

                recordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                recordBtn.classList.remove('recording');
                isRecording = false;
            };

            mediaRecorder.start();
            recordBtn.innerHTML = '<i class="fas fa-stop-circle"></i>';
            recordBtn.classList.add('recording');
            isRecording = true;
        } catch (error) {
            console.error('Error starting recording:', error);
        }
    }
});

// ✅ Fetch & Load Tasks from API
async function loadTasks() {
    try {
        const response = await fetch('http://127.0.0.1:5000/tasks');
        if (!response.ok) throw new Error('Failed to fetch tasks');

        const tasks = await response.json();
        taskList.innerHTML = ''; // Clear existing tasks

        tasks.forEach(createTaskElement);
    } catch (error) {
        console.error('Error loading tasks:', error);
    }
}

// 📝 Create Task Element (with fade-in effect)
function createTaskElement(task) {
    const li = document.createElement('li');
    li.setAttribute('data-task-id', task.id);
    li.style.animation = "fadeIn 0.3s ease-in-out";

    li.innerHTML = `
        <div class="task-content">
            <div class="task-check">
                <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} onclick="toggleTask(${task.id}, this)">
                <span class="task-text">${task.description}</span>
            </div>
            <div class="actions">
                <i class="fas fa-edit edit-icon" onclick="startEditTask(${task.id}, this)"></i>
                <i class="fas fa-trash delete-icon" onclick="deleteTask(${task.id})"></i>
            </div>
        </div>
    `;

    taskList.appendChild(li);
}

// ➕ Add New Task (with smooth fade-in)
async function addTask(description) {
    try {
        const response = await fetch('http://127.0.0.1:5000/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: description }),
        });

        if (!response.ok) throw new Error('Failed to add task');

        await loadTasks();
    } catch (error) {
        console.error('Error adding task:', error);
    }
}

// ✅ Toggle Task Completion
async function toggleTask(taskId, checkbox) {
    try {
        if (checkbox.closest('li').classList.contains('editing')) return; // Prevent toggling while editing

        const isChecked = checkbox.checked;

        const response = await fetch(`http://127.0.0.1:5000/tasks/${taskId}/toggle`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) throw new Error('Failed to update task');

        // Update task UI
        const taskText = checkbox.nextElementSibling;
        taskText.style.textDecoration = isChecked ? 'line-through' : 'none';
        taskText.style.color = isChecked ? 'rgba(255, 255, 255, 0.6)' : 'white';

    } catch (error) {
        console.error('Error updating task:', error);
    }
}

// ✏️ Start Editing Task (with smooth transition)
function startEditTask(taskId, editIcon) {
    const taskElement = editIcon.closest('li');
    taskElement.classList.add('editing');
    taskElement.style.animation = "slideIn 0.3s ease-in-out";

    const taskContent = taskElement.querySelector('.task-content');
    const taskText = taskContent.querySelector('.task-text').textContent;
    const taskCheckbox = taskContent.querySelector('.task-checkbox');

    taskContent.innerHTML = `
        <div class="task-check">
            <input type="checkbox" class="task-checkbox" ${taskCheckbox.checked ? 'checked' : ''} disabled>
            <input type="text" class="edit-input" value="${taskText}">
        </div>
        <div class="actions">
            <i class="fas fa-save save-icon" onclick="saveTask(${taskId}, this)"></i>
            <i class="fas fa-times cancel-icon" onclick="cancelEditTask(${taskId})"></i>
        </div>
    `;
}

// ❌ Cancel Editing Task (restores previous content)
function cancelEditTask(taskId) {
    const taskElement = document.querySelector(`li[data-task-id="${taskId}"]`);
    taskElement.classList.remove('editing');
    taskElement.style.animation = "fadeIn 0.3s ease-in-out";
    loadTasks();
}

// 💾 Save Edited Task (with smooth update)
async function saveTask(taskId, saveIcon) {
    try {
        const taskElement = saveIcon.closest('li');
        const newText = taskElement.querySelector('.edit-input').value;

        const response = await fetch(`http://127.0.0.1:5000/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: newText }),
        });

        if (!response.ok) throw new Error('Failed to update task');

        taskElement.style.animation = "fadeIn 0.3s ease-in-out";
        loadTasks();
    } catch (error) {
        console.error('Error updating task:', error);
    }
}

// 🗑 Delete Task
async function deleteTask(taskId) {
    try {
        const response = await fetch(`http://127.0.0.1:5000/tasks/${taskId}`, { method: 'DELETE' });
        
        if (!response.ok) throw new Error('Failed to delete task');

        await loadTasks();
    } catch (error) {
        console.error('Error deleting task:', error);
    }
}

// 🔄 Load tasks on page load
loadTasks();