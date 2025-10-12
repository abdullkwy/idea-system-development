/**
 * نظام التكامل مع CMS
 * للتفاعل مع APIs وتحديث المحتوى ديناميكياً
 */

class CMSIntegration {
    constructor() {
        this.baseURL = 'http://localhost:8000/api'; // يجب تحديثه للإنتاج
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 دقائق
        this.init();
    }

    init() {
        // تحميل المحتوى عند تحميل الصفحة
        document.addEventListener('DOMContentLoaded', () => {
            this.loadPageContent();
            this.loadBlogPosts();
            this.loadSiteSettings();
            this.setupContactForm();
            this.setupServiceForms();
            this.trackVisitor();
        });
    }

    // دالة عامة لطلبات API
    async apiRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // نظام التخزين المؤقت
    getCachedData(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }

    setCachedData(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    // تحميل محتوى الصفحة
    async loadPageContent() {
        try {
            const currentPage = this.getCurrentPageSlug();
            if (!currentPage) return;

            const cacheKey = `page_${currentPage}`;
            let pageData = this.getCachedData(cacheKey);

            if (!pageData) {
                pageData = await this.apiRequest(`/pages/${currentPage}/`);
                this.setCachedData(cacheKey, pageData);
            }

            this.updatePageContent(pageData);
        } catch (error) {
            console.error('Failed to load page content:', error);
            // الاحتفاظ بالمحتوى الثابت في حالة الفشل
        }
    }

    // تحديث محتوى الصفحة
    updatePageContent(pageData) {
        // تحديث العنوان
        const titleElement = document.querySelector('h1, .page-title, .hero-title');
        if (titleElement && pageData.title) {
            titleElement.textContent = pageData.title;
        }

        // تحديث المحتوى
        const contentElement = document.querySelector('.page-content, .hero-description, .main-content');
        if (contentElement && pageData.content) {
            contentElement.innerHTML = this.parseContent(pageData.content);
        }

        // تحديث meta tags
        this.updateMetaTags(pageData);
    }

    // تحليل المحتوى وتحويل Markdown إلى HTML
    parseContent(content) {
        if (!content) return '';
        
        // تحويل بسيط من Markdown إلى HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    // تحديث meta tags
    updateMetaTags(pageData) {
        if (pageData.meta_title) {
            document.title = pageData.meta_title;
        }

        if (pageData.meta_description) {
            let metaDesc = document.querySelector('meta[name="description"]');
            if (!metaDesc) {
                metaDesc = document.createElement('meta');
                metaDesc.name = 'description';
                document.head.appendChild(metaDesc);
            }
            metaDesc.content = pageData.meta_description;
        }
    }

    // تحميل مقالات المدونة
    async loadBlogPosts(limit = 6) {
        try {
            const cacheKey = `blog_posts_${limit}`;
            let postsData = this.getCachedData(cacheKey);

            if (!postsData) {
                postsData = await this.apiRequest(`/posts/?limit=${limit}&status=published`);
                this.setCachedData(cacheKey, postsData);
            }

            this.updateBlogSection(postsData.results || postsData);
        } catch (error) {
            console.error('Failed to load blog posts:', error);
        }
    }

    // تحديث قسم المدونة
    updateBlogSection(posts) {
        const blogContainer = document.querySelector('.blog-posts, .articles-grid, .news-section');
        if (!blogContainer || !posts.length) return;

        const postsHTML = posts.map(post => this.createBlogPostHTML(post)).join('');
        blogContainer.innerHTML = postsHTML;
    }

    // إنشاء HTML لمقال المدونة
    createBlogPostHTML(post) {
        const publishDate = new Date(post.published_at || post.created_at).toLocaleDateString('ar-SA');
        const excerpt = post.excerpt || post.content.substring(0, 150) + '...';
        const imageUrl = post.featured_image || '/assets/images/default-blog.jpg';

        return `
            <article class="blog-post-card">
                <div class="post-image">
                    <img src="${imageUrl}" alt="${post.title}" loading="lazy">
                </div>
                <div class="post-content">
                    <div class="post-meta">
                        <span class="post-date">${publishDate}</span>
                        ${post.category ? `<span class="post-category">${post.category.name}</span>` : ''}
                    </div>
                    <h3 class="post-title">
                        <a href="/blog/${post.slug}/">${post.title}</a>
                    </h3>
                    <p class="post-excerpt">${excerpt}</p>
                    <a href="/blog/${post.slug}/" class="read-more">اقرأ المزيد</a>
                </div>
            </article>
        `;
    }

    // تحميل إعدادات الموقع
    async loadSiteSettings() {
        try {
            const cacheKey = 'site_settings';
            let settings = this.getCachedData(cacheKey);

            if (!settings) {
                const settingsData = await this.apiRequest('/settings/');
                settings = settingsData.results?.[0] || settingsData;
                this.setCachedData(cacheKey, settings);
            }

            this.updateSiteSettings(settings);
        } catch (error) {
            console.error('Failed to load site settings:', error);
        }
    }

    // تحديث إعدادات الموقع
    updateSiteSettings(settings) {
        // تحديث معلومات الاتصال
        if (settings.contact_email) {
            const emailElements = document.querySelectorAll('.contact-email, [href^="mailto:"]');
            emailElements.forEach(el => {
                if (el.tagName === 'A') {
                    el.href = `mailto:${settings.contact_email}`;
                }
                el.textContent = settings.contact_email;
            });
        }

        if (settings.contact_phone) {
            const phoneElements = document.querySelectorAll('.contact-phone, [href^="tel:"]');
            phoneElements.forEach(el => {
                if (el.tagName === 'A') {
                    el.href = `tel:${settings.contact_phone}`;
                }
                el.textContent = settings.contact_phone;
            });
        }

        if (settings.address) {
            const addressElements = document.querySelectorAll('.contact-address, .address');
            addressElements.forEach(el => {
                el.textContent = settings.address;
            });
        }

        // تحديث روابط وسائل التواصل
        if (settings.social_media) {
            this.updateSocialLinks(settings.social_media);
        }
    }

    // تحديث روابط وسائل التواصل
    updateSocialLinks(socialMedia) {
        const platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube'];
        
        platforms.forEach(platform => {
            if (socialMedia[platform]) {
                const links = document.querySelectorAll(`[href*="${platform}"], .${platform}-link`);
                links.forEach(link => {
                    link.href = socialMedia[platform];
                });
            }
        });
    }

    // إعداد نموذج الاتصال
    setupContactForm() {
        const contactForm = document.querySelector('#contact-form, .contact-form');
        if (!contactForm) return;

        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.submitContactForm(contactForm);
        });
    }

    // إرسال نموذج الاتصال
    async submitContactForm(form) {
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            subject: formData.get('subject'),
            message: formData.get('message')
        };

        try {
            this.showFormLoading(form);
            
            await this.apiRequest('/contact-messages/', {
                method: 'POST',
                body: JSON.stringify(data)
            });

            this.showFormSuccess(form, 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.');
            form.reset();
        } catch (error) {
            console.error('Contact form submission failed:', error);
            this.showFormError(form, 'حدث خطأ في إرسال الرسالة. يرجى المحاولة مرة أخرى.');
        }
    }

    // إعداد نماذج الخدمات
    setupServiceForms() {
        const serviceForms = document.querySelectorAll('.service-form, [id*="request-form"]');
        
        serviceForms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.submitServiceForm(form);
            });
        });
    }

    // إرسال نموذج الخدمة
    async submitServiceForm(form) {
        const formData = new FormData(form);
        const serviceType = form.dataset.serviceType || 'general';
        
        // تحويل بيانات النموذج إلى كائن
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        try {
            this.showFormLoading(form);

            // البحث عن النموذج الديناميكي المناسب
            const dynamicForms = await this.apiRequest('/dynamic-forms/');
            const targetForm = dynamicForms.results?.find(df => 
                df.name.toLowerCase().includes(serviceType) || 
                df.slug.includes(serviceType)
            );

            if (targetForm) {
                // إرسال البيانات للنموذج الديناميكي
                await this.apiRequest('/form-submissions/', {
                    method: 'POST',
                    body: JSON.stringify({
                        form: targetForm.id,
                        data: data
                    })
                });
            } else {
                // إرسال كرسالة اتصال عادية
                await this.apiRequest('/contact-messages/', {
                    method: 'POST',
                    body: JSON.stringify({
                        name: data.name || data.client_name,
                        email: data.email,
                        phone: data.phone,
                        subject: `طلب خدمة: ${serviceType}`,
                        message: JSON.stringify(data, null, 2)
                    })
                });
            }

            this.showFormSuccess(form, 'تم إرسال طلبك بنجاح! سنتواصل معك قريباً لمناقشة التفاصيل.');
            form.reset();
        } catch (error) {
            console.error('Service form submission failed:', error);
            this.showFormError(form, 'حدث خطأ في إرسال الطلب. يرجى المحاولة مرة أخرى.');
        }
    }

    // عرض حالة التحميل للنموذج
    showFormLoading(form) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'جاري الإرسال...';
        }

        this.hideFormMessages(form);
    }

    // عرض رسالة نجاح
    showFormSuccess(form, message) {
        this.resetFormButton(form);
        this.showFormMessage(form, message, 'success');
    }

    // عرض رسالة خطأ
    showFormError(form, message) {
        this.resetFormButton(form);
        this.showFormMessage(form, message, 'error');
    }

    // إعادة تعيين زر النموذج
    resetFormButton(form) {
        const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = submitBtn.dataset.originalText || 'إرسال';
        }
    }

    // عرض رسالة النموذج
    showFormMessage(form, message, type) {
        let messageDiv = form.querySelector('.form-message');
        
        if (!messageDiv) {
            messageDiv = document.createElement('div');
            messageDiv.className = 'form-message';
            form.appendChild(messageDiv);
        }

        messageDiv.className = `form-message ${type}`;
        messageDiv.textContent = message;
        messageDiv.style.display = 'block';

        // إخفاء الرسالة بعد 5 ثوان
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }

    // إخفاء رسائل النموذج
    hideFormMessages(form) {
        const messageDiv = form.querySelector('.form-message');
        if (messageDiv) {
            messageDiv.style.display = 'none';
        }
    }

    // تتبع الزائر
    async trackVisitor() {
        try {
            const visitorData = {
                page_url: window.location.href,
                page_title: document.title,
                referrer: document.referrer,
                user_agent: navigator.userAgent,
                screen_resolution: `${screen.width}x${screen.height}`,
                language: navigator.language
            };

            await this.apiRequest('/visitor-tracking/', {
                method: 'POST',
                body: JSON.stringify(visitorData)
            });
        } catch (error) {
            console.error('Visitor tracking failed:', error);
        }
    }

    // الحصول على slug الصفحة الحالية
    getCurrentPageSlug() {
        const path = window.location.pathname;
        
        // تحويل المسار إلى slug
        if (path === '/' || path === '/index.html') {
            return 'home';
        } else if (path.includes('/about')) {
            return 'about';
        } else if (path.includes('/services')) {
            return 'services';
        } else if (path.includes('/contact')) {
            return 'contact';
        }
        
        // استخراج slug من المسار
        const segments = path.split('/').filter(segment => segment);
        return segments[segments.length - 1] || 'home';
    }

    // تحميل المحتوى الديناميكي لقسم معين
    async loadSectionContent(sectionId, contentType = 'page') {
        try {
            const cacheKey = `section_${sectionId}_${contentType}`;
            let content = this.getCachedData(cacheKey);

            if (!content) {
                if (contentType === 'page') {
                    content = await this.apiRequest(`/pages/${sectionId}/`);
                } else if (contentType === 'posts') {
                    content = await this.apiRequest(`/posts/?category=${sectionId}&limit=3`);
                }
                this.setCachedData(cacheKey, content);
            }

            return content;
        } catch (error) {
            console.error(`Failed to load ${contentType} content for ${sectionId}:`, error);
            return null;
        }
    }

    // تحديث إحصائيات الموقع
    async updateSiteStats() {
        try {
            const stats = await this.apiRequest('/analytics-reports/site-stats/');
            
            // تحديث عدادات الإحصائيات
            if (stats.visitors_count) {
                const visitorsElement = document.querySelector('.stat-visitors, .visitors-count');
                if (visitorsElement) {
                    this.animateCounter(visitorsElement, stats.visitors_count);
                }
            }

            if (stats.projects_count) {
                const projectsElement = document.querySelector('.stat-projects, .projects-count');
                if (projectsElement) {
                    this.animateCounter(projectsElement, stats.projects_count);
                }
            }

            if (stats.clients_count) {
                const clientsElement = document.querySelector('.stat-clients, .clients-count');
                if (clientsElement) {
                    this.animateCounter(clientsElement, stats.clients_count);
                }
            }
        } catch (error) {
            console.error('Failed to update site stats:', error);
        }
    }

    // تحريك العدادات
    animateCounter(element, targetValue) {
        const startValue = 0;
        const duration = 2000; // 2 ثانية
        const startTime = Date.now();

        const updateCounter = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            
            element.textContent = currentValue.toLocaleString('ar-SA');

            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };

        updateCounter();
    }
}

// تهيئة نظام CMS
const cmsIntegration = new CMSIntegration();

// تصدير للاستخدام العام
window.CMS = cmsIntegration;

