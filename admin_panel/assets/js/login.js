// إعدادات API
const API_BASE_URL = 'http://localhost:8000';

// عناصر DOM
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');

// تبديل إظهار كلمة المرور
function togglePassword() {
    const passwordField = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordField.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// إخفاء رسالة الخطأ
function hideError() {
    errorMessage.style.display = 'none';
}

// إظهار رسالة الخطأ
function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// تسجيل الدخول
async function login(username, password) {
    try {
        // محاولة الحصول على CSRF token
        const csrfResponse = await fetch(`${API_BASE_URL}/admin/login/`, {
            method: 'GET',
            credentials: 'include'
        });
        
        // استخراج CSRF token من الكوكيز
        const csrfToken = getCookie('csrftoken');
        
        // إرسال بيانات تسجيل الدخول
        const response = await fetch(`${API_BASE_URL}/admin/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: new URLSearchParams({
                'username': username,
                'password': password,
                'next': '/admin/'
            })
        });
        
        if (response.ok) {
            // تحقق من نجاح تسجيل الدخول
            const responseText = await response.text();
            if (responseText.includes('لوحة تحكم آيديا') && !responseText.includes('خطأ')) {
                // نجح تسجيل الدخول، حفظ بيانات المستخدم
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('username', username);
                
                // التوجه إلى لوحة القيادة
                window.location.href = 'dashboard.html';
                return true;
            } else {
                throw new Error('اسم المستخدم أو كلمة المرور غير صحيحة');
            }
        } else {
            throw new Error('خطأ في الاتصال بالخادم');
        }
    } catch (error) {
        console.error('خطأ في تسجيل الدخول:', error);
        throw error;
    }
}

// الحصول على قيمة الكوكي
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// معالج إرسال النموذج
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    
    // التحقق من صحة البيانات
    if (!username || !password) {
        showError('يرجى إدخال اسم المستخدم وكلمة المرور');
        return;
    }
    
    // تعطيل الزر أثناء المعالجة
    const submitBtn = loginForm.querySelector('.login-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري تسجيل الدخول...';
    submitBtn.disabled = true;
    
    try {
        await login(username, password);
    } catch (error) {
        showError(error.message || 'حدث خطأ أثناء تسجيل الدخول');
    } finally {
        // إعادة تفعيل الزر
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

// إخفاء رسالة الخطأ عند الكتابة
usernameInput.addEventListener('input', hideError);
passwordInput.addEventListener('input', hideError);

// التحقق من حالة تسجيل الدخول عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('isLoggedIn') === 'true') {
        window.location.href = 'dashboard.html';
    }
    
    // تعيين القيم الافتراضية للاختبار
    usernameInput.value = 'admin';
    passwordInput.value = 'admin123';
});

// معالجة الضغط على Enter
document.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        loginForm.dispatchEvent(new Event('submit'));
    }
});

