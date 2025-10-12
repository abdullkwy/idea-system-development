// Team Management Login JavaScript
// جافاسكريبت تسجيل دخول نظام إدارة المهام

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('teamLoginForm');
    const emailInput = document.getElementById('teamEmail');
    const passwordInput = document.getElementById('teamPassword');
    const rememberCheckbox = document.getElementById('rememberTeam');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');

    // Demo team members credentials
    const teamMembers = [
        {
            email: 'manager@ideateeam.com',
            password: 'manager123',
            name: 'أحمد محمد',
            role: 'مدير المشروع',
            id: 'TM001',
            avatar: 'manager-avatar.jpg',
            permissions: ['all']
        },
        {
            email: 'designer@ideateeam.com',
            password: 'design123',
            name: 'فاطمة علي',
            role: 'مصممة جرافيك',
            id: 'TM002',
            avatar: 'designer-avatar.jpg',
            permissions: ['design', 'creative']
        },
        {
            email: 'developer@ideateeam.com',
            password: 'dev123',
            name: 'محمد سالم',
            role: 'مطور ويب',
            id: 'TM003',
            avatar: 'developer-avatar.jpg',
            permissions: ['development', 'technical']
        },
        {
            email: 'marketer@ideateeam.com',
            password: 'market123',
            name: 'سارة أحمد',
            role: 'أخصائية تسويق',
            id: 'TM004',
            avatar: 'marketer-avatar.jpg',
            permissions: ['marketing', 'social']
        },
        {
            email: 'demo@team.com',
            password: 'demo123',
            name: 'عضو تجريبي',
            role: 'عضو فريق',
            id: 'TM005',
            avatar: 'demo-avatar.jpg',
            permissions: ['basic']
        }
    ];

    // Check for saved credentials
    const savedEmail = localStorage.getItem('teamEmail');
    const savedRemember = localStorage.getItem('teamRemember');
    
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
        const teamMember = teamMembers.find(member => member.email === email && member.password === password);
        
        if (teamMember) {
            // Save credentials if remember is checked
            if (remember) {
                localStorage.setItem('teamEmail', email);
                localStorage.setItem('teamRemember', 'true');
            } else {
                localStorage.removeItem('teamEmail');
                localStorage.removeItem('teamRemember');
            }

            // Save team member session
            sessionStorage.setItem('teamMemberData', JSON.stringify(teamMember));
            
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
        errorMessage.style.borderRightColor = '#F44336';
        
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
        errorMessage.style.borderRightColor = '#4CAF50';
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
    
    // Add role hover effects
    addRoleEffects();
});

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('teamPassword');
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
    const teamRoles = document.querySelector('.team-roles');
    
    const demoInfo = document.createElement('div');
    demoInfo.className = 'demo-info';
    demoInfo.innerHTML = `
        <div style="background: rgba(201, 167, 105, 0.1); padding: 15px; border-radius: 12px; margin-top: 20px; border-right: 4px solid #C9A769;">
            <h4 style="color: #2B5741; margin-bottom: 12px; font-size: 1rem;">بيانات تجريبية للاختبار:</h4>
            <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                <p style="font-size: 0.85rem; color: #333; margin: 0;"><strong>مدير:</strong> manager@ideateeam.com / manager123</p>
                <p style="font-size: 0.85rem; color: #333; margin: 0;"><strong>مصمم:</strong> designer@ideateeam.com / design123</p>
                <p style="font-size: 0.85rem; color: #333; margin: 0;"><strong>مطور:</strong> developer@ideateeam.com / dev123</p>
                <p style="font-size: 0.85rem; color: #333; margin: 0;"><strong>مسوق:</strong> marketer@ideateeam.com / market123</p>
                <p style="font-size: 0.85rem; color: #333; margin: 0;"><strong>تجريبي:</strong> demo@team.com / demo123</p>
            </div>
        </div>
    `;
    
    teamRoles.appendChild(demoInfo);
}

// Add role hover effects
function addRoleEffects() {
    const roleItems = document.querySelectorAll('.role-item');
    
    roleItems.forEach((item, index) => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
            this.style.boxShadow = '0 8px 20px rgba(43, 87, 65, 0.15)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = 'none';
        });
        
        // Add click effect
        item.addEventListener('click', function() {
            const roleNames = ['مدير المشروع', 'مصممة جرافيك', 'مطور ويب', 'أخصائية تسويق'];
            const emails = ['manager@ideateeam.com', 'designer@ideateeam.com', 'developer@ideateeam.com', 'marketer@ideateeam.com'];
            
            if (index < emails.length) {
                document.getElementById('teamEmail').value = emails[index];
                document.getElementById('teamEmail').focus();
            }
        });
    });
}

