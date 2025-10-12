/**
 * تفاعلات متقدمة للصفحة الرئيسية
 * رسوم متحركة وتأثيرات بصرية محسنة
 */

class EnhancedInteractions {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupScrollAnimations();
            this.setupHeroSlider();
            this.setupCounterAnimations();
            this.setupParallaxEffects();
            this.setupSmoothScrolling();
            this.setupInteractiveElements();
            this.setupLoadingAnimations();
            this.setupTypingEffect();
            this.setupFloatingElements();
        });
    }

    // إعداد الرسوم المتحركة عند التمرير
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    
                    // تشغيل العدادات عند ظهورها
                    if (entry.target.classList.contains('stat-item')) {
                        this.animateCounter(entry.target);
                    }
                }
            });
        }, observerOptions);

        // مراقبة جميع العناصر المتحركة
        document.querySelectorAll('.animate').forEach(el => {
            observer.observe(el);
        });

        // مراقبة عناصر الإحصائيات
        document.querySelectorAll('.stat-item').forEach(el => {
            observer.observe(el);
        });
    }

    // إعداد شريط تمرير Hero
    setupHeroSlider() {
        const slides = document.querySelectorAll('.hero-slide');
        const dots = document.querySelectorAll('.hero-dot');
        const prevBtn = document.querySelector('.hero-prev');
        const nextBtn = document.querySelector('.hero-next');
        
        if (!slides.length) return;

        let currentSlide = 0;
        const totalSlides = slides.length;

        const showSlide = (index) => {
            // إخفاء جميع الشرائح
            slides.forEach(slide => slide.classList.remove('active'));
            dots.forEach(dot => dot.classList.remove('active'));

            // إظهار الشريحة المحددة
            slides[index].classList.add('active');
            if (dots[index]) dots[index].classList.add('active');
        };

        const nextSlide = () => {
            currentSlide = (currentSlide + 1) % totalSlides;
            showSlide(currentSlide);
        };

        const prevSlide = () => {
            currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
            showSlide(currentSlide);
        };

        // أحداث الأزرار
        if (nextBtn) nextBtn.addEventListener('click', nextSlide);
        if (prevBtn) prevBtn.addEventListener('click', prevSlide);

        // أحداث النقاط
        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                currentSlide = index;
                showSlide(currentSlide);
            });
        });

        // التمرير التلقائي
        setInterval(nextSlide, 5000);

        // دعم لوحة المفاتيح
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') nextSlide();
            if (e.key === 'ArrowRight') prevSlide();
        });

        // دعم اللمس للأجهزة المحمولة
        let startX = 0;
        let endX = 0;

        const heroSlider = document.querySelector('.hero-slider');
        if (heroSlider) {
            heroSlider.addEventListener('touchstart', (e) => {
                startX = e.touches[0].clientX;
            });

            heroSlider.addEventListener('touchend', (e) => {
                endX = e.changedTouches[0].clientX;
                const diff = startX - endX;

                if (Math.abs(diff) > 50) {
                    if (diff > 0) {
                        nextSlide();
                    } else {
                        prevSlide();
                    }
                }
            });
        }
    }

    // تحريك العدادات
    animateCounter(statItem) {
        const numberElement = statItem.querySelector('.stat-number');
        if (!numberElement || numberElement.dataset.animated) return;

        const targetValue = parseInt(numberElement.textContent.replace(/[^\d]/g, ''));
        const duration = 2000;
        const startTime = Date.now();
        const startValue = 0;

        const updateCounter = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // استخدام easing function للحركة السلسة
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuart);
            
            numberElement.textContent = currentValue.toLocaleString('ar-SA');

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                numberElement.dataset.animated = 'true';
            }
        };

        updateCounter();
    }

    // تأثيرات المنظور (Parallax)
    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        if (!parallaxElements.length) return;

        const handleScroll = () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const rate = scrolled * (element.dataset.parallax || 0.5);
                element.style.transform = `translateY(${rate}px)`;
            });
        };

        // استخدام throttle لتحسين الأداء
        let ticking = false;
        const throttledScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', throttledScroll);
    }

    // التمرير السلس
    setupSmoothScrolling() {
        // التمرير السلس للروابط الداخلية
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // العناصر التفاعلية
    setupInteractiveElements() {
        // تأثيرات hover للبطاقات
        document.querySelectorAll('.service-card, .blog-card, .testimonial-item').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });

        // تأثيرات الأزرار
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-2px) scale(1.05)';
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0) scale(1)';
            });

            // تأثير النقر
            btn.addEventListener('mousedown', () => {
                btn.style.transform = 'translateY(0) scale(0.98)';
            });

            btn.addEventListener('mouseup', () => {
                btn.style.transform = 'translateY(-2px) scale(1.05)';
            });
        });

        // تأثيرات الأيقونات
        document.querySelectorAll('.service-icon').forEach(icon => {
            icon.addEventListener('mouseenter', () => {
                icon.style.transform = 'scale(1.2) rotate(10deg)';
            });

            icon.addEventListener('mouseleave', () => {
                icon.style.transform = 'scale(1) rotate(0deg)';
            });
        });
    }

    // رسوم متحركة للتحميل
    setupLoadingAnimations() {
        // إضافة تأثير تحميل للصور
        document.querySelectorAll('img').forEach(img => {
            if (img.complete) {
                img.classList.add('loaded');
            } else {
                img.addEventListener('load', () => {
                    img.classList.add('loaded');
                });
            }
        });

        // تأثير تحميل للمحتوى
        const content = document.querySelector('main');
        if (content) {
            setTimeout(() => {
                content.classList.add('content-loaded');
            }, 100);
        }
    }

    // تأثير الكتابة
    setupTypingEffect() {
        const typingElements = document.querySelectorAll('[data-typing]');
        
        typingElements.forEach(element => {
            const text = element.textContent;
            const speed = parseInt(element.dataset.typingSpeed) || 100;
            
            element.textContent = '';
            element.style.borderLeft = '2px solid var(--accent-color)';
            
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, speed);
                } else {
                    // إزالة المؤشر بعد انتهاء الكتابة
                    setTimeout(() => {
                        element.style.borderLeft = 'none';
                    }, 1000);
                }
            };

            // بدء التأثير عند ظهور العنصر
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        typeWriter();
                        observer.unobserve(element);
                    }
                });
            });

            observer.observe(element);
        });
    }

    // العناصر العائمة
    setupFloatingElements() {
        // إضافة عناصر ديكورية عائمة
        const createFloatingElement = (className, count = 5) => {
            for (let i = 0; i < count; i++) {
                const element = document.createElement('div');
                element.className = className;
                element.style.cssText = `
                    position: fixed;
                    pointer-events: none;
                    z-index: -1;
                    opacity: 0.1;
                    animation: float ${5 + Math.random() * 5}s ease-in-out infinite;
                    animation-delay: ${Math.random() * 5}s;
                    left: ${Math.random() * 100}%;
                    top: ${Math.random() * 100}%;
                `;
                document.body.appendChild(element);
            }
        };

        // إضافة دوائر عائمة
        const style = document.createElement('style');
        style.textContent = `
            .floating-circle {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: var(--accent-color);
            }
            
            .floating-square {
                width: 15px;
                height: 15px;
                background: var(--primary-color);
                transform: rotate(45deg);
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                33% { transform: translateY(-20px) rotate(120deg); }
                66% { transform: translateY(10px) rotate(240deg); }
            }
        `;
        document.head.appendChild(style);

        createFloatingElement('floating-circle', 3);
        createFloatingElement('floating-square', 2);
    }

    // تأثيرات الماوس
    setupMouseEffects() {
        // تأثير تتبع الماوس
        const cursor = document.createElement('div');
        cursor.className = 'custom-cursor';
        cursor.style.cssText = `
            position: fixed;
            width: 20px;
            height: 20px;
            background: var(--accent-color);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            opacity: 0.7;
            transition: transform 0.1s ease;
            transform: translate(-50%, -50%);
        `;
        document.body.appendChild(cursor);

        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX + 'px';
            cursor.style.top = e.clientY + 'px';
        });

        // تكبير المؤشر عند hover على العناصر التفاعلية
        document.querySelectorAll('a, button, .btn').forEach(element => {
            element.addEventListener('mouseenter', () => {
                cursor.style.transform = 'translate(-50%, -50%) scale(2)';
            });

            element.addEventListener('mouseleave', () => {
                cursor.style.transform = 'translate(-50%, -50%) scale(1)';
            });
        });
    }

    // تحسين الأداء
    optimizePerformance() {
        // تأجيل تحميل الصور
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));

        // تحسين الرسوم المتحركة
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        
        if (prefersReducedMotion.matches) {
            // تقليل الرسوم المتحركة للمستخدمين الذين يفضلون ذلك
            document.documentElement.style.setProperty('--transition', 'none');
        }
    }

    // إضافة تأثيرات صوتية (اختيارية)
    setupSoundEffects() {
        const playSound = (frequency, duration) => {
            if (!window.AudioContext) return;
            
            const audioContext = new AudioContext();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        };

        // أصوات للأزرار (اختيارية)
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', () => {
                playSound(800, 0.1);
            });
        });
    }

    // تهيئة جميع التحسينات
    initializeAll() {
        this.optimizePerformance();
        this.setupMouseEffects();
        // this.setupSoundEffects(); // يمكن تفعيلها حسب الحاجة
    }
}

// تهيئة النظام
const enhancedInteractions = new EnhancedInteractions();

// تصدير للاستخدام العام
window.EnhancedInteractions = enhancedInteractions;

// إضافة CSS للتحسينات
const additionalStyles = `
    .custom-cursor {
        mix-blend-mode: difference;
    }
    
    .content-loaded {
        animation: fadeIn 1s ease-out;
    }
    
    img.loaded {
        opacity: 1;
        transition: opacity 0.3s ease;
    }
    
    img:not(.loaded) {
        opacity: 0;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* تحسينات للأجهزة المحمولة */
    @media (max-width: 768px) {
        .custom-cursor {
            display: none;
        }
        
        .floating-circle,
        .floating-square {
            display: none;
        }
    }
    
    /* تحسينات للوصولية */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

