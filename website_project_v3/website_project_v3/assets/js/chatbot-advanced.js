/**
 * الشات بوت المتقدم لآيديا
 * يتكامل مع خدمة الذكاء الاصطناعي لتوفير تجربة تفاعلية ذكية
 */

class IdeaAdvancedChatbot {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.isTyping = false;
        this.chatHistory = [];
        this.apiEndpoint = 'http://localhost:5000/chat';
        this.init();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.createChatbotUI();
        this.bindEvents();
        this.showWelcomeMessage();
    }

    createChatbotUI() {
        // إنشاء زر التبديل
        const chatbotToggle = document.createElement("button");
        chatbotToggle.classList.add("chatbot-toggle", "chatbot-advanced");
        chatbotToggle.innerHTML = `
            <i class="fas fa-robot"></i>
            <span class="chatbot-badge">AI</span>
        `;
        document.body.appendChild(chatbotToggle);

        // إنشاء حاوية الشات بوت
        const chatbotContainer = document.createElement("div");
        chatbotContainer.classList.add("chatbot-container", "chatbot-advanced");
        chatbotContainer.innerHTML = `
            <div class="chatbot-header">
                <div class="chatbot-header-info">
                    <div class="chatbot-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="chatbot-title">
                        <h3>مساعد آيديا الذكي</h3>
                        <span class="chatbot-status">متصل</span>
                    </div>
                </div>
                <div class="chatbot-actions">
                    <button class="chatbot-minimize" title="تصغير">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="chatbot-close" title="إغلاق">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="chatbot-body">
                <div class="chatbot-messages"></div>
                <div class="chatbot-typing" style="display: none;">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span class="typing-text">المساعد يكتب...</span>
                </div>
            </div>
            <div class="chatbot-footer">
                <div class="chatbot-input-container">
                    <input type="text" class="chatbot-input" placeholder="اكتب رسالتك هنا..." maxlength="500">
                    <div class="chatbot-input-actions">
                        <button class="chatbot-send" title="إرسال">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
                <div class="chatbot-quick-actions">
                    <button class="quick-action" data-message="ما هي خدماتكم؟">
                        <i class="fas fa-briefcase"></i>
                        الخدمات
                    </button>
                    <button class="quick-action" data-message="كيف يمكنني طلب استشارة؟">
                        <i class="fas fa-calendar-check"></i>
                        استشارة
                    </button>
                    <button class="quick-action" data-message="ما هي أسعاركم؟">
                        <i class="fas fa-dollar-sign"></i>
                        الأسعار
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(chatbotContainer);

        // حفظ المراجع
        this.toggle = chatbotToggle;
        this.container = chatbotContainer;
        this.messagesContainer = chatbotContainer.querySelector(".chatbot-messages");
        this.input = chatbotContainer.querySelector(".chatbot-input");
        this.sendBtn = chatbotContainer.querySelector(".chatbot-send");
        this.typingIndicator = chatbotContainer.querySelector(".chatbot-typing");
        this.closeBtn = chatbotContainer.querySelector(".chatbot-close");
        this.minimizeBtn = chatbotContainer.querySelector(".chatbot-minimize");
    }

    bindEvents() {
        // تبديل الشات بوت
        this.toggle.addEventListener("click", () => {
            this.container.classList.toggle("active");
            if (this.container.classList.contains("active")) {
                this.input.focus();
            }
        });

        // إغلاق الشات بوت
        this.closeBtn.addEventListener("click", () => {
            this.container.classList.remove("active");
        });

        // تصغير الشات بوت
        this.minimizeBtn.addEventListener("click", () => {
            this.container.classList.toggle("minimized");
        });

        // إرسال الرسالة
        this.sendBtn.addEventListener("click", () => this.sendMessage());
        this.input.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // الإجراءات السريعة
        const quickActions = this.container.querySelectorAll(".quick-action");
        quickActions.forEach(action => {
            action.addEventListener("click", () => {
                const message = action.getAttribute("data-message");
                this.input.value = message;
                this.sendMessage();
            });
        });

        // تحديث حالة زر الإرسال
        this.input.addEventListener("input", () => {
            const hasText = this.input.value.trim().length > 0;
            this.sendBtn.classList.toggle("active", hasText);
        });
    }

    showWelcomeMessage() {
        const welcomeMessage = `مرحباً بك في آيديا للاستشارات والحلول التسويقية! 🎯

أنا مساعدك الذكي، وأنا هنا لمساعدتك في:
• معرفة خدماتنا وحلولنا
• الإجابة على استفساراتك
• توجيهك للحصول على استشارة مجانية

كيف يمكنني مساعدتك اليوم؟`;

        this.addMessage(welcomeMessage, "bot", true);
    }

    async sendMessage() {
        const userMessage = this.input.value.trim();
        if (!userMessage || this.isTyping) return;

        // إضافة رسالة المستخدم
        this.addMessage(userMessage, "user");
        this.input.value = "";
        this.sendBtn.classList.remove("active");

        // إظهار مؤشر الكتابة
        this.showTypingIndicator();

        try {
            // إرسال الطلب للخدمة
            const response = await this.callChatbotAPI(userMessage);
            
            // إخفاء مؤشر الكتابة
            this.hideTypingIndicator();
            
            // إضافة رد الشات بوت
            this.addMessage(response, "bot", true);
            
        } catch (error) {
            console.error("خطأ في الشات بوت:", error);
            this.hideTypingIndicator();
            
            // رسالة خطأ احتياطية
            const errorMessage = "عذراً، حدث خطأ تقني. يرجى المحاولة مرة أخرى أو التواصل معنا مباشرة على 773171477";
            this.addMessage(errorMessage, "bot", true);
        }
    }

    async callChatbotAPI(message) {
        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.status === 'error') {
            throw new Error(data.error);
        }

        return data.response;
    }

    addMessage(message, sender, animate = false) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("chatbot-message", `${sender}-message`);
        
        if (sender === "bot") {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-text">${this.formatMessage(message)}</div>
                    <div class="message-time">${this.getCurrentTime()}</div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${this.formatMessage(message)}</div>
                    <div class="message-time">${this.getCurrentTime()}</div>
                </div>
            `;
        }

        this.messagesContainer.appendChild(messageDiv);

        // تأثير الظهور
        if (animate) {
            messageDiv.style.opacity = "0";
            messageDiv.style.transform = "translateY(20px)";
            setTimeout(() => {
                messageDiv.style.transition = "all 0.3s ease";
                messageDiv.style.opacity = "1";
                messageDiv.style.transform = "translateY(0)";
            }, 100);
        }

        // التمرير للأسفل
        this.scrollToBottom();
        
        // حفظ في التاريخ
        this.chatHistory.push({ message, sender, timestamp: Date.now() });
    }

    formatMessage(message) {
        // تحويل النص إلى HTML مع دعم الأسطر الجديدة والرموز
        return message
            .replace(/\n/g, '<br>')
            .replace(/•/g, '<span class="bullet">•</span>')
            .replace(/📞|📧|🌐|🎯/g, '<span class="emoji">$&</span>');
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('ar-SA', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.style.display = "flex";
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.style.display = "none";
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    // إعادة تعيين المحادثة
    async resetConversation() {
        try {
            await fetch('http://localhost:5000/chat/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });
            
            this.messagesContainer.innerHTML = "";
            this.chatHistory = [];
            this.showWelcomeMessage();
            
        } catch (error) {
            console.error("خطأ في إعادة تعيين المحادثة:", error);
        }
    }
}

// تهيئة الشات بوت عند تحميل الصفحة
document.addEventListener("DOMContentLoaded", () => {
    // التحقق من توفر الخدمة
    fetch('http://localhost:5000/health')
        .then(response => response.json())
        .then(data => {
            console.log("✅ خدمة الشات بوت متاحة:", data);
            new IdeaAdvancedChatbot();
        })
        .catch(error => {
            console.warn("⚠️ خدمة الشات بوت غير متاحة، سيتم استخدام النسخة الأساسية");
            // تحميل الشات بوت الأساسي كبديل
            const script = document.createElement('script');
            script.src = 'assets/js/chatbot.js';
            document.head.appendChild(script);
        });
});
