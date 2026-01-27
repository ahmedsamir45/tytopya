let activeSessionId = null;
let isProcessing = false;

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const sessionsList = document.getElementById('sessions-list');
    const documentsList = document.getElementById('documents-list');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const dropArea = document.getElementById('drop-area');
    const fileElem = document.getElementById('fileElem');
    const sessionTitle = document.getElementById('session-title');

    // Initial Load
    loadSessions();

    // Event Listeners
    if (dropArea) {
        dropArea.addEventListener('click', () => fileElem.click());
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => dropArea.classList.add('highlight'), false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => dropArea.classList.remove('highlight'), false);
        });
        dropArea.addEventListener('drop', handleDrop, false);
        fileElem.addEventListener('change', function () { handleFiles(this.files); });
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // --- Session Management ---

    async function loadSessions() {
        try {
            const response = await fetch('/chat-doc/sessions');
            const sessions = await response.json();

            sessionsList.innerHTML = '';
            if (sessions.length === 0) {
                sessionsList.innerHTML = '<div class="text-center text-muted small mt-4">No chats yet.</div>';
                return;
            }

            sessions.forEach(session => {
                const item = document.createElement('div');
                item.className = `session-item ${session.id === activeSessionId ? 'active' : ''}`;
                item.dataset.id = session.id;
                item.innerHTML = `<i class="fa-regular fa-message"></i> <span class="text-truncate">${session.title}</span>`;
                item.onclick = (e) => {
                    e.preventDefault();
                    switchSession(session.id);
                };
                sessionsList.appendChild(item);
            });

            // Auto-select latest if none active
            if (!activeSessionId && sessions.length > 0) {
                switchSession(sessions[0].id);
            }
        } catch (err) {
            console.error("Load sessions failed:", err);
        }
    }

    window.createNewSession = async () => {
        try {
            const response = await fetch('/chat-doc/session/create', { method: 'POST' });
            const session = await response.json();
            activeSessionId = session.id;
            await loadSessions();
            switchSession(session.id);
        } catch (err) {
            Swal.fire('Error', 'Failed to create session', 'error');
        }
    };

    async function switchSession(sessionId) {
        if (!sessionId) return;

        console.log(`Switching to session: ${sessionId}`);
        activeSessionId = sessionId;

        // Update highlight in sidebar
        document.querySelectorAll('.session-item').forEach(el => {
            el.classList.toggle('active', parseInt(el.dataset.id) === sessionId);
        });

        try {
            const response = await fetch(`/chat-doc/session/${sessionId}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            sessionTitle.innerHTML = `<i class="fa-solid fa-robot text-primary"></i> ${data.title}`;

            // Load Documents
            renderDocuments(data.documents);

            // Load Messages
            renderMessages(data.messages);

            // Cleanup & Enable
            userInput.disabled = false;
            sendBtn.disabled = data.documents.length === 0;
            if (data.documents.length === 0) {
                userInput.placeholder = "Upload documents to start chatting...";
            } else {
                userInput.placeholder = "Ask anything about your documents...";
            }
            userInput.focus();
        } catch (err) {
            console.error("Switch session failed:", err);

            // If it's a 404, maybe the session was deleted
            if (err.message.includes('404')) {
                activeSessionId = null;
                setTimeout(loadSessions, 2000);
            }
        }
    }

    window.renameCurrentSession = async () => {
        if (!activeSessionId) return;

        const { value: newTitle } = await Swal.fire({
            title: 'Rename Chat',
            input: 'text',
            inputLabel: 'New Title',
            placeholder: 'Enter new title...',
            showCancelButton: true,
            inputValidator: (value) => {
                if (!value) return 'Title cannot be empty!';
            }
        });

        if (newTitle) {
            try {
                const response = await fetch(`/chat-doc/session/${activeSessionId}/title`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: newTitle })
                });
                if (response.ok) {
                    await loadSessions();
                    sessionTitle.innerHTML = `<i class="fa-solid fa-robot text-primary"></i> ${newTitle}`;
                }
            } catch (err) {
                Swal.fire('Error', 'Failed to rename session', 'error');
            }
        }
    };

    window.deleteCurrentSession = async () => {
        if (!activeSessionId) return;

        const result = await Swal.fire({
            title: 'Delete Chat?',
            text: "This will remove all documents and messages in this session.",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it'
        });

        if (result.isConfirmed) {
            try {
                await fetch(`/chat-doc/session/${activeSessionId}`, { method: 'DELETE' });
                activeSessionId = null;
                loadSessions();
            } catch (err) {
                Swal.fire('Error', 'Failed to delete session', 'error');
            }
        }
    };

    // --- Document Handling ---

    function handleDrop(e) {
        const dt = e.dataTransfer;
        handleFiles(dt.files);
    }

    function handleFiles(files) {
        if (!activeSessionId) {
            Swal.fire('Tip', 'Please create or select a chat session first.', 'info');
            return;
        }
        Array.from(files).forEach(uploadFile);
    }

    async function uploadFile(file) {
        const uploadStatus = document.getElementById('upload-status');
        uploadStatus.innerHTML = `<div class="spinner-border spinner-border-sm text-primary"></div> Uploading ${file.name}...`;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', activeSessionId);

        try {
            const response = await fetch('/chat-doc/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Server Error ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                uploadStatus.innerHTML = `<div class="spinner-border spinner-border-sm text-primary"></div> Processing...`;
                checkTaskStatus(data.task_id, file.name);
            } else {
                uploadStatus.innerHTML = `<span class="text-danger">Error: ${data.error}</span>`;
                console.error("Upload failed:", data);
            }
        } catch (err) {
            console.error("Upload exception:", err);
            uploadStatus.innerHTML = `<span class="text-danger">Upload failed: ${err.message}</span>`;
            Swal.fire('Upload Error', `Could not upload ${file.name}: ${err.message}`, 'error');
        }
    }

    function checkTaskStatus(taskId, fileName) {
        console.log(`Starting poll for task: ${taskId} (${fileName})`);
        const interval = setInterval(async () => {
            try {
                const r = await fetch(`/chat-doc/status/${taskId}`);
                const data = await r.json();
                console.log(`Task ${taskId} status:`, data.status);

                if (data.status === 'SUCCESS') {
                    clearInterval(interval);
                    console.log(`Task ${taskId} succeeded, refreshing session...`);
                    document.getElementById('upload-status').innerHTML = `<span class="text-success"><i class="fa-solid fa-check"></i> ${fileName} ready</span>`;
                    setTimeout(() => { document.getElementById('upload-status').innerHTML = ''; }, 3000);
                    switchSession(activeSessionId); // Refresh to show new files
                } else if (data.status === 'FAILURE' || data.status === 'REVOKED') {
                    clearInterval(interval);
                    console.error(`Task ${taskId} failed or revoked:`, data);

                    let errorMsg = "Failed to process " + fileName;
                    if (data.task_result && data.task_result.message) {
                        errorMsg += `: ${data.task_result.message}`;
                    } else if (data.task_result && data.task_result.error) {
                        errorMsg += `: ${data.task_result.error}`;
                    }

                    document.getElementById('upload-status').innerHTML = `<span class="text-danger">${errorMsg}</span>`;
                }
            } catch (err) {
                console.error(`Poll error for task ${taskId}:`, err);
                clearInterval(interval);
            }
        }, 2000);
    }

    function renderDocuments(docs) {
        if (docs.length === 0) {
            documentsList.innerHTML = '<div class="text-center text-muted py-5 small">No files in this session.</div>';
            return;
        }

        documentsList.innerHTML = '';
        docs.forEach(doc => {
            const item = document.createElement('div');
            item.className = 'doc-item';
            const icon = doc.type === 'pdf' ? 'fa-file-pdf text-danger' :
                doc.type === 'csv' ? 'fa-file-csv text-success' : 'fa-file-lines text-primary';
            item.innerHTML = `
                <i class="fa-solid ${icon}"></i>
                <div class="doc-name" title="${doc.filename}">${doc.filename}</div>
            `;
            documentsList.appendChild(item);
        });
    }

    // --- Chat ---

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text || !activeSessionId || isProcessing) return;

        addMessage("user", text);
        userInput.value = '';
        isProcessing = true;
        sendBtn.disabled = true;

        // Add "thinking" indicator
        const typingId = "typing-" + Date.now();
        const typingMsg = document.createElement('div');
        typingMsg.className = 'message bot';
        typingMsg.id = typingId;
        typingMsg.innerHTML = `<div class="message-content"><i class="fa-solid fa-ellipsis fa-fade"></i> AI is thinking...</div>`;
        chatBox.appendChild(typingMsg);
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const response = await fetch('/chat-doc/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text, session_id: activeSessionId })
            });
            const data = await response.json();

            document.getElementById(typingId).remove();

            if (data.answer) {
                addMessage("bot", data.answer);
            } else {
                addMessage("bot", "Error: " + (data.error || "Something went wrong"));
            }
        } catch (err) {
            document.getElementById(typingId).remove();
            addMessage("bot", "Network error. Is the server running?");
        } finally {
            isProcessing = false;
            sendBtn.disabled = false;
        }
    }

    function renderMessages(messages) {
        chatBox.innerHTML = '';
        if (messages.length === 0) {
            chatBox.innerHTML = `
                <div class="empty-chat-state text-center py-5">
                    <i class="fa-solid fa-comments fa-3x text-light-purple mb-3 opacity-30"></i>
                    <p class="text-muted">No messages yet. Ask a question!</p>
                </div>
            `;
            return;
        }
        messages.forEach(msg => addMessage(msg.role, msg.content, msg.timestamp));
    }

    function addMessage(sender, text, timestamp = null) {
        const emptyState = chatBox.querySelector('.empty-chat-state');
        if (emptyState) emptyState.remove();

        const div = document.createElement('div');
        div.className = `message ${sender}`;

        const time = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
            new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        div.innerHTML = `
            <div class="message-content">${text}</div>
            <div class="message-time">${time}</div>
        `;

        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

});
