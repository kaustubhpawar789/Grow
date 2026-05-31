document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container");
    const welcomeState = document.getElementById("welcome-state");
    const chatWindow = document.getElementById("chat-window");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const promptBtns = document.querySelectorAll(".prompt-btn");

    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    let chatHistory = [];
    let isFirstMessage = true;

    function formatMarkdown(text) {
        // Basic markdown-like parsing for links and italics
        return text
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="text-primary hover:underline">$1</a>')
            .replace(/\n/g, "<br>");
    }

    function addMessage(text, sender, isError = false) {
        const msgWrapper = document.createElement("div");
        const formattedText = formatMarkdown(text);
        
        if (sender === "user") {
            msgWrapper.className = "flex justify-end animate-enter mt-md";
            msgWrapper.innerHTML = `
                <div class="bg-surface-container-high text-on-surface rounded-l-xl rounded-tr-xl p-md max-w-[80%] border border-outline/10 shadow-md">
                    <p class="font-body-md text-body-md">${formattedText}</p>
                </div>
            `;
        } else {
            msgWrapper.className = "flex justify-start animate-enter mt-md";
            if (isError) {
                msgWrapper.innerHTML = `
                    <div class="flex gap-md max-w-[85%]">
                        <div class="w-10 h-10 rounded-full bg-error-container/20 flex-shrink-0 flex items-center justify-center border border-error/30">
                            <span class="material-symbols-outlined text-error text-sm">warning</span>
                        </div>
                        <div class="bg-surface-container-low text-on-surface rounded-r-xl rounded-bl-xl p-md border-l-4 border-l-error shadow-sm animate-warning-pulse">
                            <p class="font-body-md text-body-md mb-md">${formattedText}</p>
                        </div>
                    </div>
                `;
            } else {
                msgWrapper.innerHTML = `
                    <div class="flex gap-md max-w-[85%]">
                        <div class="w-10 h-10 rounded-full bg-primary/10 flex-shrink-0 flex items-center justify-center border border-primary/20">
                            <span class="material-symbols-outlined text-primary text-sm">robot_2</span>
                        </div>
                        <div class="bg-surface-container-low text-on-surface rounded-r-xl rounded-bl-xl p-md border-l-4 border-l-secondary shadow-md">
                            <p class="font-body-md text-body-md text-on-surface-variant">${formattedText}</p>
                        </div>
                    </div>
                `;
            }
        }
        
        chatWindow.appendChild(msgWrapper);
        // Scroll to bottom
        scrollToBottom();
    }

    async function sendMessage(query) {
        // Remove text from buttons if triggered from prompt
        query = query.trim();
        if (!query) return;

        if (isFirstMessage) {
            welcomeState.classList.add('hidden');
            chatWindow.classList.remove('hidden');
            isFirstMessage = false;
        }
        
        addMessage(query, "user");
        userInput.value = "";
        sendBtn.disabled = true;
        
        // Add loading indicator
        const loadingId = "loading-" + Date.now();
        const loadingDiv = document.createElement("div");
        loadingDiv.id = loadingId;
        loadingDiv.className = "flex justify-start animate-enter mt-md";
        loadingDiv.innerHTML = `
            <div class="flex gap-md max-w-[85%]">
                <div class="w-10 h-10 rounded-full bg-primary/10 flex-shrink-0 flex items-center justify-center border border-primary/20">
                    <span class="material-symbols-outlined text-primary text-sm animate-spin">sync</span>
                </div>
                <div class="bg-surface-container-low text-on-surface rounded-r-xl rounded-bl-xl p-md border-l-4 border-l-secondary shadow-md">
                    <p class="font-body-md text-body-md text-on-surface-variant">Searching verifiable facts...</p>
                </div>
            </div>
        `;
        chatWindow.appendChild(loadingDiv);
        scrollToBottom();

        try {
            const apiUrl = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1') 
                ? '/chat' 
                : 'http://localhost:8000/chat';

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, history: chatHistory })
            });
            
            document.getElementById(loadingId).remove();
            
            const data = await response.json();
            
            if (response.ok) {
                // If it's a refusal intent, treat as error for styling
                addMessage(data.response, "system", data.is_refusal);
                chatHistory.push({ role: "user", content: query });
                chatHistory.push({ role: "assistant", content: data.response });
                if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);
            } else {
                addMessage(data.detail || "An error occurred while fetching the answer.", "system", true);
            }
        } catch (error) {
            document.getElementById(loadingId).remove();
            addMessage("Error connecting to the RAG backend. Make sure the FastAPI server is running.", "system", true);
        } finally {
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        sendMessage(userInput.value);
    });

    promptBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.querySelector('p') ? btn.querySelector('p').innerText : btn.innerText;
            sendMessage(query);
        });
    });
});
