/**
 * Service Worker لتطبيق آيديا PWA
 * يوفر إمكانيات العمل دون اتصال والتحديثات التلقائية
 */

const CACHE_NAME = 'idea-pwa-v2.0';
const STATIC_CACHE = 'idea-static-v2.0';
const DYNAMIC_CACHE = 'idea-dynamic-v2.0';

// الملفات الأساسية للتخزين المؤقت
const STATIC_FILES = [
    '/',
    '/index.html',
    '/assets/css/style.css',
    '/assets/css/enhanced-design.css',
    '/assets/css/glass-morphism.css',
    '/assets/css/enhanced-gradients.css',
    '/assets/css/dark-mode.css',
    '/assets/css/navigation.css',
    '/assets/css/form-enhancements.css',
    '/assets/css/chatbot.css',
    '/assets/css/chatbot-advanced.css',
    '/assets/css/websocket-notifications.css',
    '/assets/css/responsive-improvements.css',
    '/assets/js/main.js',
    '/assets/js/enhanced-interactions.js',
    '/assets/js/lottie-animations.js',
    '/assets/js/dark-mode-toggle.js',
    '/assets/js/navigation-enhancements.js',
    '/assets/js/smart-forms.js',
    '/assets/js/chatbot-advanced.js',
    '/assets/js/websocket-client.js',
    '/assets/js/performance-optimizations.js',
    '/assets/js/mobile-optimizations.js',
    '/assets/images/logo.jpg',
    '/assets/images/hero-1.jpg',
    '/assets/images/hero-2.jpg',
    '/assets/images/hero-3.jpg',
    '/manifest.json',
    '/offline.html'
];

// الملفات الديناميكية (صفحات أخرى)
const DYNAMIC_FILES = [
    '/admin_panel/',
    '/client_portal/',
    '/team_management/',
    '/portfolio.html',
    '/request-consultancy.html'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
    console.log('🔧 تثبيت Service Worker...');
    
    event.waitUntil(
        Promise.all([
            // تخزين الملفات الأساسية
            caches.open(STATIC_CACHE).then(cache => {
                console.log('📦 تخزين الملفات الأساسية...');
                return cache.addAll(STATIC_FILES);
            }),
            
            // إنشاء التخزين المؤقت الديناميكي
            caches.open(DYNAMIC_CACHE).then(cache => {
                console.log('🔄 إنشاء التخزين المؤقت الديناميكي...');
                return Promise.resolve();
            })
        ]).then(() => {
            console.log('✅ تم تثبيت Service Worker بنجاح');
            // فرض التفعيل الفوري
            return self.skipWaiting();
        })
    );
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
    console.log('🚀 تفعيل Service Worker...');
    
    event.waitUntil(
        Promise.all([
            // حذف التخزين المؤقت القديم
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('🗑️ حذف التخزين المؤقت القديم:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // السيطرة على جميع العملاء
            self.clients.claim()
        ]).then(() => {
            console.log('✅ تم تفعيل Service Worker بنجاح');
        })
    );
});

// اعتراض طلبات الشبكة
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // تجاهل طلبات غير HTTP
    if (!request.url.startsWith('http')) {
        return;
    }
    
    // تجاهل طلبات API الخارجية
    if (url.origin !== location.origin) {
        return;
    }
    
    event.respondWith(
        handleRequest(request)
    );
});

// معالجة الطلبات
async function handleRequest(request) {
    const url = new URL(request.url);
    
    try {
        // استراتيجية Cache First للملفات الأساسية
        if (isStaticFile(url.pathname)) {
            return await cacheFirst(request);
        }
        
        // استراتيجية Network First للصفحات الديناميكية
        if (isDynamicFile(url.pathname)) {
            return await networkFirst(request);
        }
        
        // استراتيجية Stale While Revalidate للصور والأصول
        if (isAsset(url.pathname)) {
            return await staleWhileRevalidate(request);
        }
        
        // الافتراضي: Network First
        return await networkFirst(request);
        
    } catch (error) {
        console.error('خطأ في معالجة الطلب:', error);
        return await handleOffline(request);
    }
}

// التحقق من نوع الملف
function isStaticFile(pathname) {
    return STATIC_FILES.some(file => pathname.endsWith(file) || pathname === file);
}

function isDynamicFile(pathname) {
    return DYNAMIC_FILES.some(file => pathname.includes(file));
}

function isAsset(pathname) {
    return /\.(jpg|jpeg|png|gif|webp|svg|css|js|woff|woff2|ttf|eot)$/i.test(pathname);
}

// استراتيجية Cache First
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        // تحديث في الخلفية
        updateCache(request);
        return cachedResponse;
    }
    
    // إذا لم يوجد في التخزين المؤقت، جلب من الشبكة
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
        const cache = await caches.open(STATIC_CACHE);
        cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
}

// استراتيجية Network First
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            // تخزين في التخزين المؤقت الديناميكي
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        // إذا فشلت الشبكة، البحث في التخزين المؤقت
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // إذا لم يوجد، إرجاع صفحة دون اتصال
        throw error;
    }
}

// استراتيجية Stale While Revalidate
async function staleWhileRevalidate(request) {
    const cachedResponse = await caches.match(request);
    
    // تحديث في الخلفية
    const networkPromise = updateCache(request);
    
    // إرجاع النسخة المخزنة فوراً إذا وجدت
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // إذا لم توجد، انتظار الشبكة
    return await networkPromise;
}

// تحديث التخزين المؤقت في الخلفية
async function updateCache(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(
                isStaticFile(new URL(request.url).pathname) ? STATIC_CACHE : DYNAMIC_CACHE
            );
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
        
    } catch (error) {
        console.warn('فشل في تحديث التخزين المؤقت:', error);
        throw error;
    }
}

// معالجة حالة عدم الاتصال
async function handleOffline(request) {
    const url = new URL(request.url);
    
    // البحث في التخزين المؤقت أولاً
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // إذا كان طلب صفحة HTML، إرجاع صفحة دون اتصال
    if (request.headers.get('accept').includes('text/html')) {
        const offlinePage = await caches.match('/offline.html');
        if (offlinePage) {
            return offlinePage;
        }
    }
    
    // إرجاع استجابة خطأ مخصصة
    return new Response(
        JSON.stringify({
            error: 'غير متصل بالإنترنت',
            message: 'هذا المحتوى غير متاح دون اتصال',
            timestamp: new Date().toISOString()
        }),
        {
            status: 503,
            statusText: 'Service Unavailable',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            }
        }
    );
}

// معالجة رسائل من التطبيق الرئيسي
self.addEventListener('message', event => {
    const { type, payload } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0].postMessage({
                version: CACHE_NAME,
                timestamp: new Date().toISOString()
            });
            break;
            
        case 'CLEAR_CACHE':
            clearAllCaches().then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
            
        case 'CACHE_URLS':
            cacheUrls(payload.urls).then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
            
        default:
            console.warn('نوع رسالة غير معروف:', type);
    }
});

// حذف جميع التخزين المؤقت
async function clearAllCaches() {
    const cacheNames = await caches.keys();
    await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
    );
    console.log('🗑️ تم حذف جميع التخزين المؤقت');
}

// تخزين URLs محددة
async function cacheUrls(urls) {
    const cache = await caches.open(DYNAMIC_CACHE);
    await Promise.all(
        urls.map(async url => {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    await cache.put(url, response);
                }
            } catch (error) {
                console.warn(`فشل في تخزين ${url}:`, error);
            }
        })
    );
    console.log('📦 تم تخزين URLs إضافية');
}

// معالجة تحديثات الخلفية
self.addEventListener('backgroundsync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

// تنفيذ مزامنة الخلفية
async function doBackgroundSync() {
    try {
        // مزامنة البيانات المحلية مع الخادم
        console.log('🔄 تنفيذ مزامنة الخلفية...');
        
        // يمكن إضافة منطق مزامنة البيانات هنا
        // مثل إرسال النماذج المحفوظة محلياً
        
        console.log('✅ تمت مزامنة الخلفية بنجاح');
        
    } catch (error) {
        console.error('❌ فشل في مزامنة الخلفية:', error);
        throw error;
    }
}

// معالجة الإشعارات Push
self.addEventListener('push', event => {
    if (!event.data) {
        return;
    }
    
    const data = event.data.json();
    const options = {
        body: data.message || 'لديك إشعار جديد من آيديا',
        icon: '/assets/images/logo.jpg',
        badge: '/assets/images/logo.jpg',
        tag: data.tag || 'idea-notification',
        data: data.data || {},
        actions: [
            {
                action: 'open',
                title: 'فتح',
                icon: '/assets/images/logo.jpg'
            },
            {
                action: 'close',
                title: 'إغلاق'
            }
        ],
        requireInteraction: data.priority === 'high',
        silent: data.priority === 'low'
    };
    
    event.waitUntil(
        self.registration.showNotification(
            data.title || 'آيديا للاستشارات والحلول التسويقية',
            options
        )
    );
});

// معالجة النقر على الإشعارات
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    const action = event.action;
    const data = event.notification.data;
    
    if (action === 'close') {
        return;
    }
    
    // فتح التطبيق أو التنقل للصفحة المناسبة
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(clientList => {
            // البحث عن نافذة مفتوحة
            for (const client of clientList) {
                if (client.url.includes(location.origin) && 'focus' in client) {
                    return client.focus();
                }
            }
            
            // فتح نافذة جديدة
            if (clients.openWindow) {
                const targetUrl = data.url || '/';
                return clients.openWindow(targetUrl);
            }
        })
    );
});

console.log('🎯 Service Worker لآيديا PWA جاهز للعمل!');
