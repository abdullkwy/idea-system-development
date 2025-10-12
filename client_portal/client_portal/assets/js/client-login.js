// Client Portal Login JavaScript
// جافاسكريبت تسجيل دخول بوابة العملاء

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('clientLoginForm');
    const emailInput = document.getElementById('clientEmail');
    const passwordInput = document.getElementById('clientPassword');
    const rememberCheckbox = document.getElementById('rememberClient');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');

    // Demo client credentials
    const demoClients = [
        {
            email: 'client1@example.com',
            password: 'client123',
            name: 'شركة الأمل للتجارة',
            id: 'CL001'
        },
        {
            email: 'client2@example.com',
            password: 'client456',
            name: 'مؤسسة النجاح التجارية',
            id: 'CL002'
        },
        {
            email: 'demo@client.com',
            password: 'demo123',
            name: 'عميل تجريبي',
            id: 'CL003'
        }
    ];

    // Check for saved credentials
    const savedEmail = localStorage.getItem('clientEmail');
    const savedRemember = localStorage.getItem('clientRemember');
    
    if (savedEmail && savedRemember === 'true') {
        emailInput.value = savedEmail;
        rememberCheckbox.checked = true;
    }

    // Form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        const remember = rememberCheckbox.checked;

        // Validate inputs
        if (!email || !password) {
            showError('يرجى إدخال البريد الإلكتروني وكلمة المرور');
            return;
        }

        // Check credentials
        const client = demoClients.find(c => c.email === email && c.password === password);
        
        if (client) {
            // Save credentials if remember is checked
            if (remember) {
                localStorage.setItem('clientEmail', email);
                localStorage.setItem('clientRemember', 'true');
            } else {
                localStorage.removeItem('clientEmail');
                localStorage.removeItem('clientRemember');
            }

            // Save client session
            sessionStorage.setItem('clientData', JSON.stringify(client));
            
            // Show success and redirect
            showSuccess('تم تسجيل الدخول بنجاح! جاري التوجيه...');
            
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
            
        } else {
            showError('البريد الإلكتروني أو كلمة المرور غير صحيحة');
        }
    });

    // Show error message
    function showError(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.style.background = 'rgba(244, 67, 54, 0.1)';
        errorMessage.style.color = '#F44336';
        
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    // Show success message
    function showSuccess(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.style.background = 'rgba(76, 175, 80, 0.1)';
        errorMessage.style.color = '#4CAF50';
    }

    // Input validation on blur
    emailInput.addEventListener('blur', function() {
        const email = this.value.trim();
        if (email && !isValidEmail(email)) {
            this.style.borderColor = '#F44336';
        } else {
            this.style.borderColor = '#E0E0E0';
        }
    });

    // Email validation
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Add demo credentials info
    addDemoInfo();
});

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('clientPassword');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// Add demo credentials information
function addDemoInfo() {
    const helpSection = document.querySelector('.help-section');
    
    const demoInfo = document.createElement('div');
    demoInfo.className = 'demo-info';
    demoInfo.innerHTML = `
        <div style="background: rgba(201, 167, 105, 0.1); padding: 15px; border-radius: 8px; margin-top: 20px; border-right: 4px solid #C9A769;">
            <h4 style="color: #2B5741; margin-bottom: 10px; font-size: 0.95rem;">بيانات تجريبية للاختبار:</h4>
            <p style="font-size: 0.85rem; color: #333; margin-bottom: 5px;">البريد: demo@client.com</p>
            <p style="font-size: 0.85rem; color: #333;">كلمة المرور: demo123</p>
        </div>
    `;
    
    helpSection.appendChild(demoInfo);
}

