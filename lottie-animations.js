/* Lottie Animations for Idea Website */
/* رسوم متحركة Lottie لموقع آيديا */

document.addEventListener('DOMContentLoaded', () => {
    // Function to load Lottie animation
    function loadLottieAnimation(containerId, animationPath) {
        const container = document.getElementById(containerId);
        if (container) {
            lottie.loadAnimation({
                container: container, // the dom element that will contain the animation
                renderer: 'svg',
                loop: true,
                autoplay: true,
                path: animationPath // the path to the animation json
            });
        }
    }

    // Load Lottie.js library dynamically if not already loaded
    if (typeof lottie === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.10.2/lottie.min.js';
        script.onload = () => {
            // Once Lottie.js is loaded, load the animations
            // Example: loadLottieAnimation('marketing-icon', 'assets/lottie/marketing.json');
            // You will need to create/find Lottie JSON files for your icons.
            // For now, I'll add placeholders and you can replace them with actual paths.

                        loadLottieAnimation(\'consultancy-lottie-icon\', \'assets/lottie/consultancy.json\');
            loadLottieAnimation(\'marketing-lottie-icon\', \'assets/lottie/marketing.json\');
            loadLottieAnimation(\'creative-lottie-icon\', \'assets/lottie/creative.json\');
            loadLottieAnimation(\'technical-lottie-icon\', \'assets/lottie/technical.json\');
            loadLottieAnimation(\'logo-design-lottie-icon\', \'assets/lottie/logo-design.json\');
            loadLottieAnimation(\'comprehensive-lottie-icon\', \'assets/lottie/comprehensive.json\');
        };
        document.head.appendChild(script);
    } else {
        loadLottieAnimation(\'consultancy-lottie-icon\', \'assets/lottie/consultancy.json\');
        loadLottieAnimation(\'marketing-lottie-icon\', \'assets/lottie/marketing.json\');
        loadLottieAnimation(\'creative-lottie-icon\', \'assets/lottie/creative.json\');
        loadLottieAnimation(\'technical-lottie-icon\', \'assets/lottie/technical.json\');
        loadLottieAnimation(\'logo-design-lottie-icon\', \'assets/lottie/logo-design.json\');
        loadLottieAnimation(\'comprehensive-lottie-icon\', \'assets/lottie/comprehensive.json\');
    });