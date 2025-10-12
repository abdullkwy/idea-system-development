
document.addEventListener("DOMContentLoaded", () => {
    // Real-time form validation
    const forms = document.querySelectorAll("form");

    forms.forEach(form => {
        form.addEventListener("input", (event) => {
            const input = event.target;
            if (input.willValidate) {
                validateInput(input);
            }
        });

        form.addEventListener("submit", (event) => {
            let formIsValid = true;
            form.querySelectorAll("input, textarea, select").forEach(input => {
                if (input.willValidate) {
                    if (!validateInput(input)) {
                        formIsValid = false;
                    }
                }
            });
            if (!formIsValid) {
                event.preventDefault();
                alert("الرجاء تصحيح الأخطاء في النموذج قبل الإرسال.");
            }
        });
    });

    function validateInput(input) {
        if (input.checkValidity()) {
            input.classList.remove("is-invalid");
            input.classList.add("is-valid");
            showValidationMessage(input, "");
            return true;
        } else {
            input.classList.add("is-invalid");
            input.classList.remove("is-valid");
            showValidationMessage(input, input.validationMessage);
            return false;
        }
    }

    function showValidationMessage(input, message) {
        let feedback = input.nextElementSibling;
        if (!feedback || !feedback.classList.contains("invalid-feedback")) {
            feedback = document.createElement("div");
            feedback.classList.add("invalid-feedback");
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }
        feedback.textContent = message;
    }

    // Auto-save form data to localStorage
    forms.forEach(form => {
        const formId = form.id || form.name || form.action;
        if (formId) {
            // Load saved data
            const savedData = localStorage.getItem(`form_data_${formId}`);
            if (savedData) {
                const data = JSON.parse(savedData);
                for (const key in data) {
                    const input = form.elements[key];
                    if (input) {
                        if (input.type === "checkbox" || input.type === "radio") {
                            input.checked = data[key];
                        } else {
                            input.value = data[key];
                        }
                    }
                }
            }

            // Save data on input change
            form.addEventListener("input", () => {
                const formData = {};
                form.querySelectorAll("input, textarea, select").forEach(input => {
                    if (input.type === "checkbox" || input.type === "radio") {
                        formData[input.name] = input.checked;
                    } else {
                        formData[input.name] = input.value;
                    }
                });
                localStorage.setItem(`form_data_${formId}`, JSON.stringify(formData));
            });

            // Clear saved data on successful submission (optional)
            form.addEventListener("submit", () => {
                // localStorage.removeItem(`form_data_${formId}`);
            });
        }
    });

    // File upload enhancement (placeholder)
    const fileInputs = document.querySelectorAll("input[type=\"file\"]");
    fileInputs.forEach(input => {
        input.addEventListener("change", () => {
            if (input.files.length > 0) {
                console.log(`File selected: ${input.files[0].name}`);
                // Add visual feedback for file upload
            }
        });
    });

    // Multi-step form progress bar (placeholder)
    const multiStepForms = document.querySelectorAll(".multi-step-form");
    multiStepForms.forEach(form => {
        const steps = form.querySelectorAll(".form-step");
        const progressBar = form.querySelector(".form-progress-bar");
        if (steps.length > 1 && progressBar) {
            // Implement logic to update progress bar based on current step
            console.log("Multi-step form detected. Implement progress bar logic.");
        }
    });
});


