
document.addEventListener("DOMContentLoaded", () => {
    // Lazy Loading for Images
    const lazyImages = document.querySelectorAll("img.lazyload");

    if ("IntersectionObserver" in window) {
        let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    let lazyImage = entry.target;
                    lazyImage.src = lazyImage.dataset.src;
                    if (lazyImage.dataset.srcset) {
                        lazyImage.srcset = lazyImage.dataset.srcset;
                    }
                    lazyImage.classList.remove("lazyload");
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });

        lazyImages.forEach(function(lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        lazyImages.forEach(function(lazyImage) {
            lazyImage.src = lazyImage.dataset.src;
            if (lazyImage.dataset.srcset) {
                lazyImage.srcset = lazyImage.dataset.srcset;
            }
            lazyImage.classList.remove("lazyload");
        });
    }

    // Optimize images (Note: This is typically done server-side or during build process)
    // For client-side, we can ensure WebP support and fallback.
    function supportsWebP() {
        const elem = document.createElement("canvas");
        if (elem.getContext && elem.getContext("2d")) {
            return elem.toDataURL("image/webp").indexOf("data:image/webp") === 0;
        }
        return false;
    }

    if (supportsWebP()) {
        document.body.classList.add("webp");
    } else {
        document.body.classList.add("no-webp");
    }

    // Preload important pages (example: home, services)
    const pagesToPreload = [
        "/",
        "/consultancy.html",
        "/marketing-solutions.html"
    ];

    pagesToPreload.forEach(url => {
        const link = document.createElement("link");
        link.rel = "preload";
        link.as = "document";
        link.href = url;
        document.head.appendChild(link);
    });

    // Critical CSS (This is usually inlined in HTML or handled by build tools)
    // For demonstration, we can add a class to body when critical CSS is loaded
    document.body.classList.add("critical-css-loaded");

    // Service Worker for caching (requires HTTPS)
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
            navigator.serviceWorker.register("/service-worker.js")
                .then(registration => {
                    console.log("Service Worker registered with scope:", registration.scope);
                })
                .catch(error => {
                    console.error("Service Worker registration failed:", error);
                });
        });
    }
});


