// SEO Optimization JavaScript
// جافاسكريبت تحسين محركات البحث

document.addEventListener('DOMContentLoaded', function() {
    // Initialize SEO optimizations
    initSEOOptimizations();
    setupDynamicMetaTags();
    optimizeImages();
    setupStructuredData();
    setupSocialSharing();
});

// Initialize SEO optimizations
function initSEOOptimizations() {
    // Update page title dynamically
    updatePageTitle();
    
    // Add canonical URL
    addCanonicalURL();
    
    // Optimize internal linking
    optimizeInternalLinks();
    
    // Setup breadcrumbs
    setupBreadcrumbs();
    
    // Add alt text to images
    addAltTextToImages();
    
    // Optimize headings structure
    optimizeHeadingsStructure();
}

// Update page title dynamically
function updatePageTitle() {
    const currentPage = getCurrentPage();
    const baseTitle = 'آيديا للاستشارات والحلول التسويقية';
    
    const pageTitles = {
        'index': 'آيديا للاستشارات والحلول التسويقية - خبراء التسويق والإبداع',
        'about': 'من نحن - آيديا للاستشارات والحلول التسويقية',
        'services': 'حلولنا التسويقية - آيديا للاستشارات والحلول التسويقية',
        'consultancy': 'الاستشارات التسويقية - آيديا للاستشارات والحلول التسويقية',
        'marketing': 'الحلول التسويقية - آيديا للاستشارات والحلول التسويقية',
        'creative': 'الحلول الإبداعية - آيديا للاستشارات والحلول التسويقية',
        'technical': 'الحلول التقنية - آيديا للاستشارات والحلول التسويقية',
        'portfolio': 'أعمالنا - آيديا للاستشارات والحلول التسويقية',
        'clients': 'عملاؤنا - آيديا للاستشارات والحلول التسويقية',
        'blog': 'مدونة التسويق - آيديا للاستشارات والحلول التسويقية',
        'contact': 'تواصل معنا - آيديا للاستشارات والحلول التسويقية'
    };
    
    const newTitle = pageTitles[currentPage] || baseTitle;
    document.title = newTitle;
}

// Get current page name
function getCurrentPage() {
    const path = window.location.pathname;
    const fileName = path.split('/').pop().replace('.html', '') || 'index';
    return fileName;
}

// Add canonical URL
function addCanonicalURL() {
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
        canonical = document.createElement('link');
        canonical.rel = 'canonical';
        document.head.appendChild(canonical);
    }
    canonical.href = window.location.href.split('?')[0].split('#')[0];
}

// Setup dynamic meta tags
function setupDynamicMetaTags() {
    const currentPage = getCurrentPage();
    
    const pageDescriptions = {
        'index': 'آيديا للاستشارات والحلول التسويقية، شركة متخصصة في تقديم حلول تسويقية متكاملة تجمع بين الإبداع والرؤية الاستراتيجية والتنفيذ الدقيق. أوسع مما تتخيل أدق مما تتوقع.',
        'about': 'تعرف على آيديا للاستشارات والحلول التسويقية، فريقنا المتخصص، رؤيتنا ورسالتنا في تقديم أفضل الحلول التسويقية المبتكرة.',
        'consultancy': 'احصل على استشارات تسويقية متخصصة من خبراء آيديا. نقدم استشارات استراتيجية شاملة لتطوير أعمالك وتحقيق أهدافك التسويقية.',
        'marketing': 'حلول تسويقية متكاملة تشمل التسويق الرقمي، إدارة وسائل التواصل الاجتماعي، والحملات الإعلانية المبتكرة.',
        'creative': 'حلول إبداعية تشمل تصميم الهوية البصرية، تصميم الشعارات، والمحتوى الإبداعي الذي يميز علامتك التجارية.',
        'technical': 'حلول تقنية متطورة تشمل تطوير المواقع الإلكترونية، التطبيقات، وأنظمة إدارة المحتوى.',
        'portfolio': 'استعرض أعمالنا ومشاريعنا الناجحة في مختلف المجالات التسويقية والإبداعية والتقنية.',
        'clients': 'تعرف على عملائنا وشركائنا في النجاح من مختلف القطاعات والصناعات.',
        'blog': 'مدونة التسويق - مقالات ونصائح تسويقية من خبراء آيديا لتطوير استراتيجياتك التسويقية.',
        'contact': 'تواصل مع فريق آيديا للاستشارات والحلول التسويقية. نحن هنا لمساعدتك في تحقيق أهدافك التسويقية.'
    };
    
    const pageKeywords = {
        'index': 'آيديا، استشارات تسويقية، حلول تسويقية، تسويق رقمي، تصميم إبداعي، تطوير مواقع، اليمن، صنعاء',
        'about': 'من نحن، فريق آيديا، رؤية آيديا، رسالة آيديا، خبراء التسويق',
        'consultancy': 'استشارات تسويقية، استراتيجية تسويقية، خطة تسويقية، استشارة مجانية',
        'marketing': 'تسويق رقمي، وسائل التواصل الاجتماعي، حملات إعلانية، تسويق إلكتروني',
        'creative': 'تصميم جرافيك، هوية بصرية، تصميم شعار، محتوى إبداعي، تصميم إعلانات',
        'technical': 'تطوير مواقع، تطبيقات جوال، أنظمة إدارة محتوى، برمجة',
        'portfolio': 'أعمالنا، مشاريع آيديا، نماذج أعمال، معرض الأعمال',
        'clients': 'عملاء آيديا، شركاء النجاح، قصص نجاح، شهادات العملاء',
        'blog': 'مدونة التسويق، مقالات تسويقية، نصائح تسويقية، أخبار التسويق',
        'contact': 'تواصل معنا، اتصل بنا، عنوان آيديا، أرقام التواصل'
    };
    
    // Update meta description
    updateMetaTag('description', pageDescriptions[currentPage] || pageDescriptions['index']);
    
    // Update meta keywords
    updateMetaTag('keywords', pageKeywords[currentPage] || pageKeywords['index']);
    
    // Update Open Graph tags
    updateOpenGraphTags(currentPage);
    
    // Update Twitter Card tags
    updateTwitterCardTags(currentPage);
}

// Update meta tag
function updateMetaTag(name, content) {
    let metaTag = document.querySelector(`meta[name="${name}"]`);
    if (!metaTag) {
        metaTag = document.createElement('meta');
        metaTag.name = name;
        document.head.appendChild(metaTag);
    }
    metaTag.content = content;
}

// Update Open Graph tags
function updateOpenGraphTags(currentPage) {
    const baseURL = window.location.origin;
    const currentURL = window.location.href;
    
    const ogTags = {
        'og:title': document.title,
        'og:description': document.querySelector('meta[name="description"]')?.content || '',
        'og:url': currentURL,
        'og:type': 'website',
        'og:site_name': 'آيديا للاستشارات والحلول التسويقية',
        'og:image': `${baseURL}/assets/images/og-image.jpg`,
        'og:image:width': '1200',
        'og:image:height': '630',
        'og:locale': 'ar_SA'
    };
    
    Object.entries(ogTags).forEach(([property, content]) => {
        updateMetaProperty(property, content);
    });
}

// Update Twitter Card tags
function updateTwitterCardTags(currentPage) {
    const baseURL = window.location.origin;
    
    const twitterTags = {
        'twitter:card': 'summary_large_image',
        'twitter:site': '@ideamarketing',
        'twitter:creator': '@ideamarketing',
        'twitter:title': document.title,
        'twitter:description': document.querySelector('meta[name="description"]')?.content || '',
        'twitter:image': `${baseURL}/assets/images/twitter-card.jpg`
    };
    
    Object.entries(twitterTags).forEach(([name, content]) => {
        updateMetaTag(name, content);
    });
}

// Update meta property
function updateMetaProperty(property, content) {
    let metaTag = document.querySelector(`meta[property="${property}"]`);
    if (!metaTag) {
        metaTag = document.createElement('meta');
        metaTag.setAttribute('property', property);
        document.head.appendChild(metaTag);
    }
    metaTag.content = content;
}

// Optimize images for SEO
function optimizeImages() {
    const images = document.querySelectorAll('img');
    
    images.forEach((img, index) => {
        // Add alt text if missing
        if (!img.alt) {
            const altTexts = {
                'logo': 'شعار آيديا للاستشارات والحلول التسويقية',
                'service': `خدمة ${index + 1} - آيديا للاستشارات والحلول التسويقية`,
                'team': `عضو فريق آيديا ${index + 1}`,
                'client': `عميل آيديا ${index + 1}`,
                'portfolio': `مشروع آيديا ${index + 1}`
            };
            
            // Determine image type based on src or class
            let imageType = 'service';
            if (img.src.includes('logo')) imageType = 'logo';
            else if (img.classList.contains('team-image')) imageType = 'team';
            else if (img.classList.contains('client-logo')) imageType = 'client';
            else if (img.classList.contains('portfolio-image')) imageType = 'portfolio';
            
            img.alt = altTexts[imageType];
        }
        
        // Add loading="lazy" for better performance
        if (!img.hasAttribute('loading')) {
            img.loading = 'lazy';
        }
        
        // Add title attribute for better accessibility
        if (!img.title && img.alt) {
            img.title = img.alt;
        }
    });
}

// Setup structured data
function setupStructuredData() {
    const structuredData = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "آيديا للاستشارات والحلول التسويقية",
        "alternateName": "آيديا",
        "url": window.location.origin,
        "logo": `${window.location.origin}/assets/images/logo.jpg`,
        "description": "آيديا للاستشارات والحلول التسويقية، شركة متخصصة في تقديم حلول تسويقية متكاملة تجمع بين الإبداع والرؤية الاستراتيجية والتنفيذ الدقيق",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "حدة - امام الديرة مول - مبنى القطرية - الدور الخامس",
            "addressLocality": "صنعاء",
            "addressCountry": "اليمن"
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+967-773171477",
            "contactType": "customer service",
            "availableLanguage": "Arabic"
        },
        "sameAs": [
            "https://www.facebook.com/ideamarketing",
            "https://www.twitter.com/ideamarketing",
            "https://www.instagram.com/ideamarketing",
            "https://www.linkedin.com/company/ideamarketing"
        ],
        "foundingDate": "2020",
        "numberOfEmployees": "10-50",
        "slogan": "أوسع مما تتخيل أدق مما تتوقع",
        "serviceArea": {
            "@type": "Country",
            "name": "اليمن"
        },
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "حلول آيديا التسويقية",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "itemOffered": {
                        "@type": "Service",
                        "name": "الاستشارات التسويقية",
                        "description": "استشارات تسويقية متخصصة لتطوير استراتيجيات التسويق"
                    }
                },
                {
                    "@type": "Offer",
                    "itemOffered": {
                        "@type": "Service",
                        "name": "الحلول التسويقية",
                        "description": "حلول تسويقية متكاملة تشمل التسويق الرقمي وإدارة وسائل التواصل"
                    }
                },
                {
                    "@type": "Offer",
                    "itemOffered": {
                        "@type": "Service",
                        "name": "الحلول الإبداعية",
                        "description": "تصميم الهوية البصرية والمحتوى الإبداعي"
                    }
                },
                {
                    "@type": "Offer",
                    "itemOffered": {
                        "@type": "Service",
                        "name": "الحلول التقنية",
                        "description": "تطوير المواقع والتطبيقات وأنظمة إدارة المحتوى"
                    }
                }
            ]
        }
    };
    
    // Add or update structured data script
    let structuredDataScript = document.querySelector('script[type="application/ld+json"]');
    if (!structuredDataScript) {
        structuredDataScript = document.createElement('script');
        structuredDataScript.type = 'application/ld+json';
        document.head.appendChild(structuredDataScript);
    }
    
    structuredDataScript.textContent = JSON.stringify(structuredData, null, 2);
}

// Optimize internal links
function optimizeInternalLinks() {
    const links = document.querySelectorAll('a[href^="/"], a[href^="./"], a[href^="../"]');
    
    links.forEach(link => {
        // Add title attribute if missing
        if (!link.title && link.textContent.trim()) {
            link.title = link.textContent.trim();
        }
        
        // Add rel="noopener" for external links opening in new tab
        if (link.target === '_blank' && !link.rel.includes('noopener')) {
            link.rel = link.rel ? `${link.rel} noopener` : 'noopener';
        }
    });
}

// Setup breadcrumbs
function setupBreadcrumbs() {
    const currentPage = getCurrentPage();
    const breadcrumbContainer = document.querySelector('.breadcrumbs');
    
    if (!breadcrumbContainer) {
        return;
    }
    
    const breadcrumbPaths = {
        'index': [{ name: 'الرئيسية', url: 'index.html' }],
        'about': [
            { name: 'الرئيسية', url: 'index.html' },
            { name: 'من نحن', url: 'about.html' }
        ],
        'consultancy': [
            { name: 'الرئيسية', url: 'index.html' },
            { name: 'حلول آيديا', url: '#' },
            { name: 'الاستشارات التسويقية', url: 'consultancy.html' }
        ],
        'marketing': [
            { name: 'الرئيسية', url: 'index.html' },
            { name: 'حلول آيديا', url: '#' },
            { name: 'الحلول التسويقية', url: 'marketing.html' }
        ],
        'creative': [
            { name: 'الرئيسية', url: 'index.html' },
            { name: 'حلول آيديا', url: '#' },
            { name: 'الحلول الإبداعية', url: 'creative.html' }
        ],
        'technical': [
            { name: 'الرئيسية', url: 'index.html' },
            { name: 'حلول آيديا', url: '#' },
            { name: 'الحلول التقنية', url: 'technical.html' }
        ]
    };
    
    const breadcrumbs = breadcrumbPaths[currentPage] || breadcrumbPaths['index'];
    
    // Generate breadcrumb HTML
    const breadcrumbHTML = breadcrumbs.map((crumb, index) => {
        if (index === breadcrumbs.length - 1) {
            return `<span class="breadcrumb-current">${crumb.name}</span>`;
        } else {
            return `<a href="${crumb.url}" class="breadcrumb-link">${crumb.name}</a>`;
        }
    }).join(' <span class="breadcrumb-separator">></span> ');
    
    breadcrumbContainer.innerHTML = breadcrumbHTML;
    
    // Add structured data for breadcrumbs
    const breadcrumbStructuredData = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": breadcrumbs.map((crumb, index) => ({
            "@type": "ListItem",
            "position": index + 1,
            "name": crumb.name,
            "item": crumb.url !== '#' ? `${window.location.origin}/${crumb.url}` : undefined
        }))
    };
    
    // Add breadcrumb structured data
    const breadcrumbScript = document.createElement('script');
    breadcrumbScript.type = 'application/ld+json';
    breadcrumbScript.textContent = JSON.stringify(breadcrumbStructuredData, null, 2);
    document.head.appendChild(breadcrumbScript);
}

// Add alt text to images
function addAltTextToImages() {
    const images = document.querySelectorAll('img:not([alt])');
    
    images.forEach((img, index) => {
        // Generate meaningful alt text based on context
        let altText = '';
        
        if (img.closest('.service-card')) {
            const serviceTitle = img.closest('.service-card').querySelector('h3')?.textContent;
            altText = serviceTitle ? `أيقونة ${serviceTitle}` : `خدمة آيديا ${index + 1}`;
        } else if (img.closest('.team-card')) {
            const memberName = img.closest('.team-card').querySelector('h4')?.textContent;
            altText = memberName ? `صورة ${memberName}` : `عضو فريق آيديا ${index + 1}`;
        } else if (img.closest('.testimonial-card')) {
            const clientName = img.closest('.testimonial-card').querySelector('.client-name')?.textContent;
            altText = clientName ? `صورة ${clientName}` : `عميل آيديا ${index + 1}`;
        } else if (img.src.includes('logo')) {
            altText = 'شعار آيديا للاستشارات والحلول التسويقية';
        } else {
            altText = `صورة آيديا للاستشارات والحلول التسويقية ${index + 1}`;
        }
        
        img.alt = altText;
    });
}

// Optimize headings structure
function optimizeHeadingsStructure() {
    const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let currentLevel = 0;
    
    headings.forEach(heading => {
        const level = parseInt(heading.tagName.substring(1));
        
        // Ensure proper heading hierarchy
        if (level > currentLevel + 1) {
            console.warn(`Heading hierarchy issue: ${heading.tagName} follows h${currentLevel}`);
        }
        
        currentLevel = level;
        
        // Add id for anchor links if missing
        if (!heading.id && heading.textContent.trim()) {
            const id = heading.textContent.trim()
                .replace(/\s+/g, '-')
                .replace(/[^\w\u0600-\u06FF-]/g, '')
                .toLowerCase();
            heading.id = id;
        }
    });
}

// Setup social sharing
function setupSocialSharing() {
    const shareButtons = document.querySelectorAll('.share-button');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.dataset.platform;
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            const description = encodeURIComponent(
                document.querySelector('meta[name="description"]')?.content || ''
            );
            
            let shareUrl = '';
            
            switch (platform) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
                    break;
                case 'linkedin':
                    shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
                    break;
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${title}%20${url}`;
                    break;
                case 'telegram':
                    shareUrl = `https://t.me/share/url?url=${url}&text=${title}`;
                    break;
            }
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
}

// Track page views for analytics
function trackPageView() {
    // Google Analytics tracking (if implemented)
    if (typeof gtag !== 'undefined') {
        gtag('config', 'GA_MEASUREMENT_ID', {
            page_title: document.title,
            page_location: window.location.href
        });
    }
    
    // Custom analytics tracking
    const pageData = {
        page: getCurrentPage(),
        title: document.title,
        url: window.location.href,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        referrer: document.referrer
    };
    
    // Send to analytics endpoint (if available)
    if (typeof fetch !== 'undefined') {
        fetch('/api/analytics/pageview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pageData)
        }).catch(error => {
            console.log('Analytics tracking failed:', error);
        });
    }
}

// Initialize page tracking
trackPageView();

// Export functions for use in other scripts
window.SEOOptimizer = {
    updatePageTitle,
    setupDynamicMetaTags,
    optimizeImages,
    setupStructuredData,
    trackPageView
};

