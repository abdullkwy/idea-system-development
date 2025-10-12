// Social Media Integration JavaScript
// جافاسكريبت تكامل منصات التواصل الاجتماعي

document.addEventListener('DOMContentLoaded', function() {
    // Initialize social integrations
    initSocialIntegrations();
    setupSocialSharing();
    setupSocialLogin();
    setupSocialFeeds();
    setupSocialPixels();
});

// Initialize social integrations
function initSocialIntegrations() {
    // Load Facebook SDK
    loadFacebookSDK();
    
    // Load Twitter widgets
    loadTwitterWidgets();
    
    // Load Instagram embed
    loadInstagramEmbed();
    
    // Load LinkedIn insights
    loadLinkedInInsights();
    
    // Setup social sharing buttons
    setupSocialSharingButtons();
}

// Load Facebook SDK
function loadFacebookSDK() {
    window.fbAsyncInit = function() {
        FB.init({
            appId: 'YOUR_FACEBOOK_APP_ID', // Replace with actual app ID
            cookie: true,
            xfbml: true,
            version: 'v18.0'
        });
        
        // Track Facebook events
        FB.Event.subscribe('edge.create', function(url) {
            trackSocialAction('facebook', 'like', url);
        });
        
        FB.Event.subscribe('edge.remove', function(url) {
            trackSocialAction('facebook', 'unlike', url);
        });
        
        FB.Event.subscribe('message.send', function(url) {
            trackSocialAction('facebook', 'send', url);
        });
    };
    
    // Load Facebook SDK script
    (function(d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) return;
        js = d.createElement(s); js.id = id;
        js.src = "https://connect.facebook.net/ar_AR/sdk.js";
        fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
}

// Load Twitter widgets
function loadTwitterWidgets() {
    window.twttr = (function(d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0],
            t = window.twttr || {};
        if (d.getElementById(id)) return t;
        js = d.createElement(s);
        js.id = id;
        js.src = "https://platform.twitter.com/widgets.js";
        fjs.parentNode.insertBefore(js, fjs);
        
        t._e = [];
        t.ready = function(f) {
            t._e.push(f);
        };
        
        return t;
    }(document, "script", "twitter-wjs"));
    
    // Track Twitter events
    twttr.ready(function(twttr) {
        twttr.events.bind('tweet', function(event) {
            trackSocialAction('twitter', 'tweet', event.target.src);
        });
        
        twttr.events.bind('follow', function(event) {
            trackSocialAction('twitter', 'follow', event.data.screen_name);
        });
    });
}

// Load Instagram embed
function loadInstagramEmbed() {
    const script = document.createElement('script');
    script.src = '//www.instagram.com/embed.js';
    script.async = true;
    document.head.appendChild(script);
}

// Load LinkedIn insights
function loadLinkedInInsights() {
    const script = document.createElement('script');
    script.src = 'https://platform.linkedin.com/in.js';
    script.type = 'text/javascript';
    script.innerHTML = 'lang: ar_AE';
    document.head.appendChild(script);
}

// Setup social sharing
function setupSocialSharing() {
    const shareButtons = document.querySelectorAll('.social-share-btn');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.dataset.platform;
            const url = encodeURIComponent(this.dataset.url || window.location.href);
            const title = encodeURIComponent(this.dataset.title || document.title);
            const description = encodeURIComponent(
                this.dataset.description || 
                document.querySelector('meta[name="description"]')?.content || 
                ''
            );
            const image = encodeURIComponent(
                this.dataset.image || 
                document.querySelector('meta[property="og:image"]')?.content || 
                ''
            );
            
            shareTo(platform, url, title, description, image);
            
            // Track sharing event
            trackSocialAction(platform, 'share', url);
        });
    });
}

// Share to specific platform
function shareTo(platform, url, title, description, image) {
    let shareUrl = '';
    let windowFeatures = 'width=600,height=400,scrollbars=yes,resizable=yes';
    
    switch (platform) {
        case 'facebook':
            shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${title}`;
            break;
            
        case 'twitter':
            const twitterText = title.length > 240 ? title.substring(0, 237) + '...' : title;
            shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${twitterText}&via=ideamarketing`;
            break;
            
        case 'linkedin':
            shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}&summary=${description}`;
            break;
            
        case 'whatsapp':
            shareUrl = `https://wa.me/?text=${title}%20${url}`;
            windowFeatures = 'width=400,height=600';
            break;
            
        case 'telegram':
            shareUrl = `https://t.me/share/url?url=${url}&text=${title}`;
            break;
            
        case 'pinterest':
            shareUrl = `https://pinterest.com/pin/create/button/?url=${url}&media=${image}&description=${title}`;
            break;
            
        case 'reddit':
            shareUrl = `https://reddit.com/submit?url=${url}&title=${title}`;
            break;
            
        case 'email':
            const emailSubject = encodeURIComponent(`مشاركة: ${decodeURIComponent(title)}`);
            const emailBody = encodeURIComponent(`أردت مشاركة هذا الرابط معك:\n\n${decodeURIComponent(title)}\n${decodeURIComponent(url)}\n\n${decodeURIComponent(description)}`);
            shareUrl = `mailto:?subject=${emailSubject}&body=${emailBody}`;
            window.location.href = shareUrl;
            return;
            
        case 'copy':
            copyToClipboard(decodeURIComponent(url));
            showCopyNotification();
            return;
    }
    
    if (shareUrl) {
        window.open(shareUrl, 'share', windowFeatures);
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            console.log('URL copied to clipboard');
        }).catch(function(err) {
            console.error('Failed to copy URL: ', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

// Fallback copy method
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        console.log('URL copied to clipboard (fallback)');
    } catch (err) {
        console.error('Fallback copy failed: ', err);
    }
    
    document.body.removeChild(textArea);
}

// Show copy notification
function showCopyNotification() {
    const notification = document.createElement('div');
    notification.className = 'copy-notification';
    notification.textContent = 'تم نسخ الرابط!';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 6px;
        z-index: 10000;
        font-family: 'Tajawal', sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Setup social sharing buttons
function setupSocialSharingButtons() {
    // Add floating social share buttons
    const floatingShare = document.createElement('div');
    floatingShare.className = 'floating-social-share';
    floatingShare.innerHTML = `
        <div class="share-toggle" id="shareToggle">
            <i class="fas fa-share-alt"></i>
        </div>
        <div class="share-options" id="shareOptions">
            <button class="social-share-btn" data-platform="facebook" title="مشاركة على فيسبوك">
                <i class="fab fa-facebook-f"></i>
            </button>
            <button class="social-share-btn" data-platform="twitter" title="مشاركة على تويتر">
                <i class="fab fa-twitter"></i>
            </button>
            <button class="social-share-btn" data-platform="linkedin" title="مشاركة على لينكد إن">
                <i class="fab fa-linkedin-in"></i>
            </button>
            <button class="social-share-btn" data-platform="whatsapp" title="مشاركة على واتساب">
                <i class="fab fa-whatsapp"></i>
            </button>
            <button class="social-share-btn" data-platform="telegram" title="مشاركة على تيليجرام">
                <i class="fab fa-telegram-plane"></i>
            </button>
            <button class="social-share-btn" data-platform="copy" title="نسخ الرابط">
                <i class="fas fa-link"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(floatingShare);
    
    // Add CSS for floating share
    const shareStyles = document.createElement('style');
    shareStyles.textContent = `
        .floating-social-share {
            position: fixed;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            z-index: 1000;
        }
        
        .share-toggle {
            width: 50px;
            height: 50px;
            background: var(--primary-color);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
            margin-bottom: 10px;
        }
        
        .share-toggle:hover {
            transform: scale(1.1);
            background: var(--primary-dark);
        }
        
        .share-options {
            display: flex;
            flex-direction: column;
            gap: 8px;
            opacity: 0;
            visibility: hidden;
            transform: translateY(10px);
            transition: all 0.3s ease;
        }
        
        .share-options.active {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }
        
        .social-share-btn {
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }
        
        .social-share-btn[data-platform="facebook"] { background: #1877f2; }
        .social-share-btn[data-platform="twitter"] { background: #1da1f2; }
        .social-share-btn[data-platform="linkedin"] { background: #0077b5; }
        .social-share-btn[data-platform="whatsapp"] { background: #25d366; }
        .social-share-btn[data-platform="telegram"] { background: #0088cc; }
        .social-share-btn[data-platform="copy"] { background: var(--secondary-color); }
        
        .social-share-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        
        @media (max-width: 768px) {
            .floating-social-share {
                left: 10px;
            }
            
            .share-toggle {
                width: 45px;
                height: 45px;
            }
            
            .social-share-btn {
                width: 35px;
                height: 35px;
                font-size: 0.8rem;
            }
        }
    `;
    
    document.head.appendChild(shareStyles);
    
    // Setup toggle functionality
    const shareToggle = document.getElementById('shareToggle');
    const shareOptions = document.getElementById('shareOptions');
    
    shareToggle.addEventListener('click', function() {
        shareOptions.classList.toggle('active');
    });
    
    // Close when clicking outside
    document.addEventListener('click', function(e) {
        if (!floatingShare.contains(e.target)) {
            shareOptions.classList.remove('active');
        }
    });
    
    // Re-setup event listeners for new buttons
    setupSocialSharing();
}

// Setup social login
function setupSocialLogin() {
    const socialLoginButtons = document.querySelectorAll('.social-login-btn');
    
    socialLoginButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.dataset.platform;
            
            switch (platform) {
                case 'facebook':
                    loginWithFacebook();
                    break;
                case 'google':
                    loginWithGoogle();
                    break;
                case 'twitter':
                    loginWithTwitter();
                    break;
            }
        });
    });
}

// Login with Facebook
function loginWithFacebook() {
    if (typeof FB !== 'undefined') {
        FB.login(function(response) {
            if (response.authResponse) {
                FB.api('/me', {fields: 'name,email'}, function(response) {
                    handleSocialLogin('facebook', response);
                });
            }
        }, {scope: 'email'});
    }
}

// Login with Google
function loginWithGoogle() {
    // Implement Google Sign-In
    console.log('Google login not implemented yet');
}

// Login with Twitter
function loginWithTwitter() {
    // Implement Twitter login
    console.log('Twitter login not implemented yet');
}

// Handle social login response
function handleSocialLogin(platform, userData) {
    console.log(`${platform} login successful:`, userData);
    
    // Send login data to server
    fetch('/api/social-login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            platform: platform,
            userData: userData
        })
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            // Redirect or update UI
            window.location.reload();
        }
    }).catch(error => {
        console.error('Social login error:', error);
    });
}

// Setup social feeds
function setupSocialFeeds() {
    // Load Instagram feed
    loadInstagramFeed();
    
    // Load Twitter timeline
    loadTwitterTimeline();
    
    // Load Facebook page plugin
    loadFacebookPagePlugin();
}

// Load Instagram feed
function loadInstagramFeed() {
    const instagramContainer = document.getElementById('instagram-feed');
    if (instagramContainer) {
        // Use Instagram Basic Display API or third-party service
        // This is a placeholder for Instagram feed implementation
        instagramContainer.innerHTML = `
            <div class="instagram-placeholder">
                <p>Instagram feed will be loaded here</p>
                <a href="https://www.instagram.com/ideamarketing" target="_blank" class="btn btn-primary">
                    <i class="fab fa-instagram"></i>
                    تابعنا على Instagram
                </a>
            </div>
        `;
    }
}

// Load Twitter timeline
function loadTwitterTimeline() {
    const twitterContainer = document.getElementById('twitter-timeline');
    if (twitterContainer) {
        twitterContainer.innerHTML = `
            <a class="twitter-timeline" 
               data-lang="ar" 
               data-height="400" 
               data-theme="light" 
               href="https://twitter.com/ideamarketing?ref_src=twsrc%5Etfw">
               Tweets by ideamarketing
            </a>
        `;
        
        // Reload Twitter widgets
        if (typeof twttr !== 'undefined') {
            twttr.widgets.load();
        }
    }
}

// Load Facebook page plugin
function loadFacebookPagePlugin() {
    const facebookContainer = document.getElementById('facebook-page');
    if (facebookContainer) {
        facebookContainer.innerHTML = `
            <div class="fb-page" 
                 data-href="https://www.facebook.com/ideamarketing" 
                 data-tabs="timeline" 
                 data-width="340" 
                 data-height="400" 
                 data-small-header="false" 
                 data-adapt-container-width="true" 
                 data-hide-cover="false" 
                 data-show-facepile="true">
                <blockquote cite="https://www.facebook.com/ideamarketing" class="fb-xfbml-parse-ignore">
                    <a href="https://www.facebook.com/ideamarketing">آيديا للاستشارات والحلول التسويقية</a>
                </blockquote>
            </div>
        `;
        
        // Parse Facebook elements
        if (typeof FB !== 'undefined') {
            FB.XFBML.parse();
        }
    }
}

// Setup social pixels
function setupSocialPixels() {
    // Facebook Pixel
    setupFacebookPixel();
    
    // Twitter Pixel
    setupTwitterPixel();
    
    // LinkedIn Insight Tag
    setupLinkedInPixel();
}

// Setup Facebook Pixel
function setupFacebookPixel() {
    !function(f,b,e,v,n,t,s)
    {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
    n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    
    fbq('init', 'YOUR_FACEBOOK_PIXEL_ID'); // Replace with actual pixel ID
    fbq('track', 'PageView');
}

// Setup Twitter Pixel
function setupTwitterPixel() {
    !function(e,t,n,s,u,a){e.twq||(s=e.twq=function(){s.exe?s.exe.apply(s,arguments):s.queue.push(arguments);
    },s.version='1.1',s.queue=[],u=t.createElement(n),u.async=!0,u.src='//static.ads-twitter.com/uwt.js',
    a=t.getElementsByTagName(n)[0],a.parentNode.insertBefore(u,a))}(window,document,'script');
    
    twq('init','YOUR_TWITTER_PIXEL_ID'); // Replace with actual pixel ID
    twq('track','PageView');
}

// Setup LinkedIn Pixel
function setupLinkedInPixel() {
    _linkedin_partner_id = "YOUR_LINKEDIN_PARTNER_ID"; // Replace with actual partner ID
    window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
    window._linkedin_data_partner_ids.push(_linkedin_partner_id);
    
    (function(l) {
        if (!l){window.lintrk = function(a,b){window.lintrk.q.push([a,b])};
        window.lintrk.q=[]}
        var s = document.getElementsByTagName("script")[0];
        var b = document.createElement("script");
        b.type = "text/javascript";b.async = true;
        b.src = "https://snap.licdn.com/li.lms-analytics/insight.min.js";
        s.parentNode.insertBefore(b, s);})(window.lintrk);
}

// Track social action
function trackSocialAction(platform, action, target) {
    // Track with Google Analytics
    if (typeof gtag !== 'undefined') {
        gtag('event', 'social_action', {
            social_network: platform,
            social_action: action,
            social_target: target
        });
    }
    
    // Track with custom analytics
    if (typeof window.IdeaAnalytics !== 'undefined' && window.IdeaAnalytics.trackEvent) {
        window.IdeaAnalytics.trackEvent('social_action', {
            platform: platform,
            action: action,
            target: target,
            timestamp: Date.now()
        });
    }
    
    console.log(`Social action tracked: ${platform} - ${action} - ${target}`);
}

// Export social functions
window.SocialIntegration = {
    shareTo,
    trackSocialAction,
    copyToClipboard
};

