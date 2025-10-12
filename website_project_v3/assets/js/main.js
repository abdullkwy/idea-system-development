// الانتظار حتى يتم تحميل المستند بالكامل
document.addEventListener('DOMContentLoaded', function() {
    // تفعيل القائمة المتنقلة للهواتف المحمولة
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // تفعيل القوائم المنسدلة في الهواتف المحمولة
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const link = dropdown.querySelector('.nav-link');
        
        link.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                dropdown.classList.toggle('active');
            }
        });
    });
    
    // تفعيل الدردشة المباشرة
    const chatButton = document.querySelector('.chat-button');
    const chatPopup = document.querySelector('.chat-popup');
    const chatClose = document.querySelector('.chat-close');
    const chatInput = document.querySelector('.chat-input');
    const chatSend = document.querySelector('.chat-send');
    const chatBody = document.querySelector('.chat-body');
    
    if (chatButton && chatPopup) {
        chatButton.addEventListener('click', function() {
            chatPopup.style.display = 'block';
        });
        
        chatClose.addEventListener('click', function() {
            chatPopup.style.display = 'none';
        });
        
        // إرسال رسالة في الدردشة
        function sendMessage() {
            const message = chatInput.value.trim();
            
            if (message !== '') {
                // إضافة رسالة المستخدم
                const userMessage = document.createElement('div');
                userMessage.className = 'chat-message sent';
                userMessage.innerHTML = `<div class="chat-bubble">${message}</div>`;
                chatBody.appendChild(userMessage);
                
                // مسح حقل الإدخال
                chatInput.value = '';
                
                // تمرير الدردشة إلى الأسفل
                chatBody.scrollTop = chatBody.scrollHeight;
                
                // محاكاة رد آلي بعد ثانية واحدة
                setTimeout(function() {
                    const botMessage = document.createElement('div');
                    botMessage.className = 'chat-message received';
                    botMessage.innerHTML = `<div class="chat-bubble">شكراً لتواصلك معنا! سيقوم أحد ممثلي خدمة العملاء بالرد عليك قريباً.</div>`;
                    chatBody.appendChild(botMessage);
                    
                    // تمرير الدردشة إلى الأسفل
                    chatBody.scrollTop = chatBody.scrollHeight;
                }, 1000);
            }
        }
        
        chatSend.addEventListener('click', sendMessage);
        
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
    
    // تفعيل فلتر معرض الأعمال
    const filterButtons = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    
    if (filterButtons.length > 0 && portfolioItems.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // إزالة الفئة النشطة من جميع الأزرار
                filterButtons.forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // إضافة الفئة النشطة للزر المحدد
                this.classList.add('active');
                
                const filter = this.getAttribute('data-filter');
                
                // تصفية العناصر
                portfolioItems.forEach(item => {
                    if (filter === 'all' || item.getAttribute('data-category') === filter) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // تفعيل نموذج حجز الاستشارات
    const consultationForm = document.querySelector('.consultation-form');
    
    if (consultationForm) {
        consultationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // محاكاة إرسال النموذج
            const submitButton = consultationForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            
            submitButton.disabled = true;
            submitButton.textContent = 'جاري الإرسال...';
            
            setTimeout(function() {
                submitButton.textContent = 'تم الإرسال بنجاح!';
                
                // إعادة تعيين النموذج
                consultationForm.reset();
                
                // إعادة زر الإرسال إلى حالته الأصلية بعد 3 ثوانٍ
                setTimeout(function() {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }, 3000);
            }, 1500);
        });
    }
    
    // تفعيل نموذج طلب تصميم الشعار
    const logoDesignForm = document.querySelector('.logo-design-form');
    
    if (logoDesignForm) {
        // تفعيل اختيار الألوان
        const colorOptions = document.querySelectorAll('.color-option');
        
        colorOptions.forEach(option => {
            option.addEventListener('click', function() {
                // إذا كان متعدد الاختيارات
                if (this.parentElement.classList.contains('multiple-select')) {
                    this.classList.toggle('selected');
                } else {
                    // إزالة التحديد من جميع الخيارات
                    colorOptions.forEach(opt => {
                        if (opt.parentElement === this.parentElement) {
                            opt.classList.remove('selected');
                        }
                    });
                    
                    // تحديد الخيار المحدد
                    this.classList.add('selected');
                }
            });
        });
        
        // إرسال النموذج
        logoDesignForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // محاكاة إرسال النموذج
            const submitButton = logoDesignForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            
            submitButton.disabled = true;
            submitButton.textContent = 'جاري الإرسال...';
            
            setTimeout(function() {
                submitButton.textContent = 'تم إرسال طلبك بنجاح!';
                
                // إعادة تعيين النموذج
                logoDesignForm.reset();
                
                // إعادة زر الإرسال إلى حالته الأصلية بعد 3 ثوانٍ
                setTimeout(function() {
                    submitButton.disabled = false;
                    submitButton.textContent = originalText;
                }, 3000);
            }, 1500);
        });
    }
    
    // تفعيل التأثيرات الحركية عند التمرير
    const animatedElements = document.querySelectorAll('.animate');
    
    function checkIfInView() {
        animatedElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                element.classList.add('visible');
            }
        });
    }
    
    // تشغيل الفحص عند التمرير
    window.addEventListener('scroll', checkIfInView);
    
    // تشغيل الفحص عند تحميل الصفحة
    checkIfInView();
    
    // تفعيل زر العودة إلى الأعلى
    const scrollTopButton = document.querySelector('.scroll-top');
    
    if (scrollTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollTopButton.style.display = 'flex';
            } else {
                scrollTopButton.style.display = 'none';
            }
        });
        
        scrollTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});
