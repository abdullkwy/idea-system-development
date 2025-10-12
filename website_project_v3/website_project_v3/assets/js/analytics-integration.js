// Analytics Integration JavaScript
// جافاسكريبت تكامل التحليلات والأداء

document.addEventListener('DOMContentLoaded', function() {
    // Initialize analytics
    initAnalytics();
    setupEventTracking();
    setupPerformanceMonitoring();
    setupUserBehaviorTracking();
    setupConversionTracking();
});

// Initialize analytics
function initAnalytics() {
    // Initialize Google Analytics (if available)
    initGoogleAnalytics();
    
    // Initialize custom analytics
    initCustomAnalytics();
    
    // Setup heat mapping (if available)
    setupHeatMapping();
    
    // Track initial page load
    trackPageLoad();
}

// Initialize Google Analytics
function initGoogleAnalytics() {
    // Check if Google Analytics is already loaded
    if (typeof gtag !== 'undefined') {
        return;
    }
    
    // Load Google Analytics script
    const gaScript = document.createElement('script');
    gaScript.async = true;
    gaScript.src = 'https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID';
    document.head.appendChild(gaScript);
    
    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'GA_MEASUREMENT_ID', {
        send_page_view: false // We'll send custom page views
    });
    
    window.gtag = gtag;
}

// Initialize custom analytics
function initCustomAnalytics() {
    // Create analytics object
    window.IdeaAnalytics = {
        sessionId: generateSessionId(),
        userId: getUserId(),
        startTime: Date.now(),
        events: [],
        pageViews: [],
        interactions: []
    };
    
    // Track session start
    trackEvent('session_start', {
        session_id: window.IdeaAnalytics.sessionId,
        user_agent: navigator.userAgent,
        screen_resolution: `${screen.width}x${screen.height}`,
        viewport_size: `${window.innerWidth}x${window.innerHeight}`,
        language: navigator.language,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    });
}

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Get or create user ID
function getUserId() {
    let userId = localStorage.getItem('idea_user_id');
    if (!userId) {
        userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('idea_user_id', userId);
    }
    return userId;
}

// Setup event tracking
function setupEventTracking() {
    // Track button clicks
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, .btn, a');
        if (target) {
            const eventData = {
                element_type: target.tagName.toLowerCase(),
                element_class: target.className,
                element_text: target.textContent.trim().substring(0, 100),
                element_id: target.id,
                page_url: window.location.href,
                timestamp: Date.now()
            };
            
            if (target.classList.contains('btn-primary')) {
                trackEvent('cta_click', eventData);
            } else if (target.classList.contains('nav-link')) {
                trackEvent('navigation_click', eventData);
            } else if (target.href && target.href.includes('tel:')) {
                trackEvent('phone_click', eventData);
            } else if (target.href && target.href.includes('mailto:')) {
                trackEvent('email_click', eventData);
            } else {
                trackEvent('click', eventData);
            }
        }
    });
    
    // Track form submissions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.tagName === 'FORM') {
            const formData = new FormData(form);
            const eventData = {
                form_id: form.id,
                form_class: form.className,
                form_action: form.action,
                form_method: form.method,
                field_count: form.elements.length,
                page_url: window.location.href,
                timestamp: Date.now()
            };
            
            trackEvent('form_submit', eventData);
        }
    });
    
    // Track scroll depth
    let maxScrollDepth = 0;
    let scrollCheckpoints = [25, 50, 75, 90, 100];
    let trackedCheckpoints = [];
    
    window.addEventListener('scroll', throttle(function() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        const scrollPercent = Math.round((scrollTop / docHeight) * 100);
        
        if (scrollPercent > maxScrollDepth) {
            maxScrollDepth = scrollPercent;
        }
        
        scrollCheckpoints.forEach(checkpoint => {
            if (scrollPercent >= checkpoint && !trackedCheckpoints.includes(checkpoint)) {
                trackedCheckpoints.push(checkpoint);
                trackEvent('scroll_depth', {
                    depth_percent: checkpoint,
                    page_url: window.location.href,
                    timestamp: Date.now()
                });
            }
        });
    }, 1000));
    
    // Track time on page
    let timeOnPage = 0;
    const timeTracker = setInterval(function() {
        timeOnPage += 10;
        
        // Track engagement milestones
        if (timeOnPage === 30) {
            trackEvent('engagement_30s', { time_on_page: timeOnPage });
        } else if (timeOnPage === 60) {
            trackEvent('engagement_1m', { time_on_page: timeOnPage });
        } else if (timeOnPage === 180) {
            trackEvent('engagement_3m', { time_on_page: timeOnPage });
        }
    }, 10000); // Check every 10 seconds
    
    // Clear interval on page unload
    window.addEventListener('beforeunload', function() {
        clearInterval(timeTracker);
        trackEvent('page_exit', {
            time_on_page: timeOnPage,
            max_scroll_depth: maxScrollDepth,
            page_url: window.location.href
        });
        
        // Send any pending analytics data
        sendAnalyticsData();
    });
}

// Setup performance monitoring
function setupPerformanceMonitoring() {
    // Track page load performance
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            if (perfData) {
                trackEvent('page_performance', {
                    load_time: Math.round(perfData.loadEventEnd - perfData.fetchStart),
                    dom_content_loaded: Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart),
                    first_paint: getFirstPaint(),
                    largest_contentful_paint: getLargestContentfulPaint(),
                    cumulative_layout_shift: getCumulativeLayoutShift(),
                    page_url: window.location.href
                });
            }
        }, 1000);
    });
    
    // Track resource loading errors
    window.addEventListener('error', function(e) {
        if (e.target !== window) {
            trackEvent('resource_error', {
                resource_type: e.target.tagName,
                resource_src: e.target.src || e.target.href,
                error_message: e.message,
                page_url: window.location.href
            });
        }
    });
    
    // Track JavaScript errors
    window.addEventListener('error', function(e) {
        if (e.target === window) {
            trackEvent('javascript_error', {
                error_message: e.message,
                error_filename: e.filename,
                error_line: e.lineno,
                error_column: e.colno,
                page_url: window.location.href
            });
        }
    });
}

// Get First Paint timing
function getFirstPaint() {
    const paintEntries = performance.getEntriesByType('paint');
    const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
    return firstPaint ? Math.round(firstPaint.startTime) : null;
}

// Get Largest Contentful Paint
function getLargestContentfulPaint() {
    return new Promise(resolve => {
        const observer = new PerformanceObserver(list => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1];
            resolve(Math.round(lastEntry.startTime));
        });
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
        
        // Fallback timeout
        setTimeout(() => resolve(null), 5000);
    });
}

// Get Cumulative Layout Shift
function getCumulativeLayoutShift() {
    let clsValue = 0;
    const observer = new PerformanceObserver(list => {
        for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
                clsValue += entry.value;
            }
        }
    });
    observer.observe({ entryTypes: ['layout-shift'] });
    
    setTimeout(() => {
        observer.disconnect();
    }, 5000);
    
    return clsValue;
}

// Setup user behavior tracking
function setupUserBehaviorTracking() {
    // Track mouse movements (heatmap data)
    let mousePositions = [];
    document.addEventListener('mousemove', throttle(function(e) {
        mousePositions.push({
            x: e.clientX,
            y: e.clientY,
            timestamp: Date.now()
        });
        
        // Limit stored positions
        if (mousePositions.length > 100) {
            mousePositions = mousePositions.slice(-50);
        }
    }, 100));
    
    // Track clicks for heatmap
    document.addEventListener('click', function(e) {
        trackEvent('click_position', {
            x: e.clientX,
            y: e.clientY,
            element_tag: e.target.tagName,
            element_class: e.target.className,
            page_url: window.location.href,
            viewport_width: window.innerWidth,
            viewport_height: window.innerHeight
        });
    });
    
    // Track device and browser info
    const deviceInfo = {
        user_agent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        screen_width: screen.width,
        screen_height: screen.height,
        viewport_width: window.innerWidth,
        viewport_height: window.innerHeight,
        color_depth: screen.colorDepth,
        pixel_ratio: window.devicePixelRatio,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        connection_type: navigator.connection ? navigator.connection.effectiveType : 'unknown'
    };
    
    trackEvent('device_info', deviceInfo);
}

// Setup conversion tracking
function setupConversionTracking() {
    // Track form completions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.tagName === 'FORM') {
            const formType = getFormType(form);
            trackEvent('conversion', {
                type: 'form_completion',
                form_type: formType,
                form_id: form.id,
                page_url: window.location.href,
                timestamp: Date.now()
            });
            
            // Track specific conversion types
            if (formType === 'consultation') {
                trackEvent('consultation_request', {
                    source: 'website_form',
                    page_url: window.location.href
                });
            } else if (formType === 'contact') {
                trackEvent('contact_form_submit', {
                    source: 'website_form',
                    page_url: window.location.href
                });
            }
        }
    });
    
    // Track phone number clicks
    document.addEventListener('click', function(e) {
        const target = e.target.closest('a[href^="tel:"]');
        if (target) {
            trackEvent('conversion', {
                type: 'phone_call_intent',
                phone_number: target.href.replace('tel:', ''),
                page_url: window.location.href,
                timestamp: Date.now()
            });
        }
    });
    
    // Track email clicks
    document.addEventListener('click', function(e) {
        const target = e.target.closest('a[href^="mailto:"]');
        if (target) {
            trackEvent('conversion', {
                type: 'email_intent',
                email: target.href.replace('mailto:', ''),
                page_url: window.location.href,
                timestamp: Date.now()
            });
        }
    });
}

// Get form type
function getFormType(form) {
    if (form.id.includes('consultation') || form.action.includes('consultation')) {
        return 'consultation';
    } else if (form.id.includes('contact') || form.action.includes('contact')) {
        return 'contact';
    } else if (form.id.includes('quote') || form.action.includes('quote')) {
        return 'quote';
    } else {
        return 'general';
    }
}

// Track custom event
function trackEvent(eventName, eventData = {}) {
    const event = {
        name: eventName,
        data: eventData,
        timestamp: Date.now(),
        session_id: window.IdeaAnalytics?.sessionId,
        user_id: window.IdeaAnalytics?.userId,
        page_url: window.location.href,
        page_title: document.title
    };
    
    // Add to local storage
    if (window.IdeaAnalytics) {
        window.IdeaAnalytics.events.push(event);
    }
    
    // Send to Google Analytics if available
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, eventData);
    }
    
    // Send to custom analytics endpoint
    sendEventToAnalytics(event);
    
    console.log('Analytics Event:', eventName, eventData);
}

// Track page load
function trackPageLoad() {
    const pageData = {
        page_url: window.location.href,
        page_title: document.title,
        referrer: document.referrer,
        timestamp: Date.now(),
        session_id: window.IdeaAnalytics?.sessionId,
        user_id: window.IdeaAnalytics?.userId
    };
    
    trackEvent('page_view', pageData);
    
    if (window.IdeaAnalytics) {
        window.IdeaAnalytics.pageViews.push(pageData);
    }
}

// Send event to analytics endpoint
function sendEventToAnalytics(event) {
    // Use sendBeacon for better reliability
    if (navigator.sendBeacon) {
        const data = JSON.stringify(event);
        navigator.sendBeacon('/api/analytics/event', data);
    } else {
        // Fallback to fetch
        fetch('/api/analytics/event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(event)
        }).catch(error => {
            console.log('Analytics send failed:', error);
        });
    }
}

// Send all analytics data
function sendAnalyticsData() {
    if (window.IdeaAnalytics && window.IdeaAnalytics.events.length > 0) {
        const data = {
            session_id: window.IdeaAnalytics.sessionId,
            user_id: window.IdeaAnalytics.userId,
            events: window.IdeaAnalytics.events,
            page_views: window.IdeaAnalytics.pageViews,
            session_duration: Date.now() - window.IdeaAnalytics.startTime
        };
        
        if (navigator.sendBeacon) {
            navigator.sendBeacon('/api/analytics/session', JSON.stringify(data));
        }
    }
}

// Setup heat mapping
function setupHeatMapping() {
    // Simple heatmap data collection
    const heatmapData = {
        clicks: [],
        scrollDepth: [],
        timeSpent: []
    };
    
    // Collect click data
    document.addEventListener('click', function(e) {
        heatmapData.clicks.push({
            x: e.clientX,
            y: e.clientY,
            element: e.target.tagName,
            timestamp: Date.now()
        });
    });
    
    // Send heatmap data periodically
    setInterval(function() {
        if (heatmapData.clicks.length > 0) {
            sendEventToAnalytics({
                name: 'heatmap_data',
                data: heatmapData,
                timestamp: Date.now()
            });
            
            // Clear data after sending
            heatmapData.clicks = [];
        }
    }, 30000); // Send every 30 seconds
}

// Utility function: throttle
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Export analytics functions
window.IdeaAnalytics = window.IdeaAnalytics || {};
window.IdeaAnalytics.trackEvent = trackEvent;
window.IdeaAnalytics.trackPageLoad = trackPageLoad;
window.IdeaAnalytics.sendAnalyticsData = sendAnalyticsData;

