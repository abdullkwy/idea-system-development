
document.addEventListener("DOMContentLoaded", () => {
    const chatbotToggle = document.createElement("button");
    chatbotToggle.classList.add("chatbot-toggle");
    chatbotToggle.innerHTML = 
        `<i class="fas fa-comments"></i>`;
    document.body.appendChild(chatbotToggle);

    const chatbotContainer = document.createElement("div");
    chatbotContainer.classList.add("chatbot-container");
    chatbotContainer.innerHTML = `
        <div class="chatbot-header">
            <h3>مساعد آيديا</h3>
            <button class="chatbot-close"><i class="fas fa-times"></i></button>
        </div>
        <div class="chatbot-body">
            <div class="chatbot-message bot-message">مرحباً! كيف يمكنني مساعدتك اليوم؟</div>
        </div>
        <div class="chatbot-footer">
            <input type="text" class="chatbot-input" placeholder="اكتب رسالتك...">
            <button class="chatbot-send"><i class="fas fa-paper-plane"></i></button>
        </div>
    `;
    document.body.appendChild(chatbotContainer);

    const chatbotInput = chatbotContainer.querySelector(".chatbot-input");
    const chatbotSendBtn = chatbotContainer.querySelector(".chatbot-send");
    const chatbotBody = chatbotContainer.querySelector(".chatbot-body");
    const chatbotCloseBtn = chatbotContainer.querySelector(".chatbot-close");

    let chatbotResponses = {};

    // Load chatbot responses from JSON file
    fetch("assets/data/chatbot-responses.json")
        .then(response => response.json())
        .then(data => {
            chatbotResponses = data.responses;
        })
        .catch(error => console.error("Error loading chatbot responses:", error));

    chatbotToggle.addEventListener("click", () => {
        chatbotContainer.classList.toggle("active");
    });

    chatbotCloseBtn.addEventListener("click", () => {
        chatbotContainer.classList.remove("active");
    });

    function sendMessage() {
        const userMessage = chatbotInput.value.trim();
        if (userMessage === "") return;

        appendMessage(userMessage, "user-message");
        chatbotInput.value = "";

        // Simulate bot response
        setTimeout(() => {
            const botResponse = getBotResponse(userMessage);
            appendMessage(botResponse, "bot-message");
            chatbotBody.scrollTop = chatbotBody.scrollHeight; // Scroll to bottom
        }, 500);
    }

    chatbotSendBtn.addEventListener("click", sendMessage);
    chatbotInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

    function appendMessage(message, type) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("chatbot-message", type);
        messageDiv.textContent = message;
        chatbotBody.appendChild(messageDiv);
    }

    function getBotResponse(userMessage) {
        userMessage = userMessage.toLowerCase();

        if (userMessage.includes("مرحبا") || userMessage.includes("سلام")) {
            return getRandomResponse(chatbotResponses.greeting);
        } else if (userMessage.includes("خدمات") || userMessage.includes("ماذا تقدمون")) {
            return getRandomResponse(chatbotResponses.services);
        } else if (userMessage.includes("اسعار") || userMessage.includes("تكلفة")) {
            return getRandomResponse(chatbotResponses.pricing);
        } else if (userMessage.includes("تواصل") || userMessage.includes("اتصل")) {
            return getRandomResponse(chatbotResponses.contact);
        } else {
            return "عذراً، لم أفهم سؤالك. هل يمكنك إعادة الصياغة؟";
        }
    }

    function getRandomResponse(responsesArray) {
        if (!responsesArray || responsesArray.length === 0) {
            return "لا توجد إجابات متاحة حالياً.";
        }
        const randomIndex = Math.floor(Math.random() * responsesArray.length);
        return responsesArray[randomIndex];
    }
});


