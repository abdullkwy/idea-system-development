/* Dark Mode Toggle for Idea Website */
/* تبديل الوضع الليلي لموقع آيديا */

document.addEventListener("DOMContentLoaded", () => {
    const toggleButton = document.createElement("button");
    toggleButton.classList.add("dark-mode-toggle");
    toggleButton.innerHTML = 
        `<i class="fas fa-sun"></i>
         <i class="fas fa-moon"></i>`;
    document.body.appendChild(toggleButton);

    // Check for saved preference or system preference
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    const currentTheme = localStorage.getItem("theme");

    if (currentTheme === "dark") {
        document.body.classList.add("dark-mode");
        toggleButton.classList.add("dark");
    } else if (currentTheme === "light") {
        document.body.classList.remove("dark-mode");
        toggleButton.classList.remove("dark");
    } else if (prefersDarkScheme.matches) {
        document.body.classList.add("dark-mode");
        toggleButton.classList.add("dark");
    }

    // Listen for changes in system preference
    prefersDarkScheme.addEventListener("change", (e) => {
        if (e.matches) {
            document.body.classList.add("dark-mode");
            toggleButton.classList.add("dark");
            localStorage.setItem("theme", "dark");
        } else {
            document.body.classList.remove("dark-mode");
            toggleButton.classList.remove("dark");
            localStorage.setItem("theme", "light");
        }
    });

    // Toggle on button click
    toggleButton.addEventListener("click", () => {
        document.body.classList.toggle("dark-mode");
        toggleButton.classList.toggle("dark");
        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }
    });
});


