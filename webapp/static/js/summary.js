// Make functions global so inline onclick works
window.toggleInput = function (type) {
    const textSection = document.getElementById('textInputSection');
    const pdfSection = document.getElementById('pdfInputSection');

    if (type === 'text') {
        textSection.style.display = 'block';
        pdfSection.style.display = 'none';
    } else {
        textSection.style.display = 'none';
        pdfSection.style.display = 'block';
    }
};

window.toggleSettings = function () {
    const panels = document.getElementById('settingsPanel');
    if (panels) panels.style.display = panels.style.display === 'none' ? 'block' : 'none';
};

window.showLoading = function () {
    const btn = document.querySelector('.btn-generate');
    if (btn) {
        const text = btn.querySelector('.btn-text');
        const loader = btn.querySelector('.loader');
        if (text) text.innerText = "Processing...";
        if (loader) loader.style.display = 'inline-block';
        btn.style.opacity = '0.7';
    }
};

window.hideLoading = function () {
    const btn = document.querySelector('.btn-generate');
    if (btn) {
        const text = btn.querySelector('.btn-text');
        const loader = btn.querySelector('.loader');
        if (text) text.innerText = "Generate Summary";
        if (loader) loader.style.display = 'none';
        btn.style.opacity = '1';
    }
};

window.paste = async function () {
    const textS = document.getElementById("textS");
    try {
        const text = await navigator.clipboard.readText();
        if (textS) textS.value = text;
    } catch (err) {
        console.error('Failed to read clipboard: ', err);
        // Fallback for older browsers or strict permissions
        if (textS) {
            textS.placeholder = "Please use Ctrl+V to paste";
            textS.focus();
        }
    }
};

window.copyToClipboard = function (elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;

    if (navigator.clipboard) {
        navigator.clipboard.writeText(el.innerText).then(() => {
            const btn = document.querySelector(`[onclick="copyToClipboard('${elementId}')"]`);
            if (btn) {
                const original = btn.innerHTML;
                btn.innerHTML = '<i class="fa-solid fa-check"></i>';
                setTimeout(() => btn.innerHTML = original, 2000);
            }
        }).catch(err => {
            console.error('Async: Could not copy text: ', err);
            fallbackCopy(el.innerText);
        });
    } else {
        fallbackCopy(el.innerText);
    }
};

function fallbackCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        alert('Copied to clipboard!');
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }
    document.body.removeChild(textarea);
}

// Typing Effect
function typeWriter(element, text, speed = 10) {
    if (!element || !text) return;
    element.textContent = "";
    let i = 0;
    const timer = setInterval(() => {
        element.textContent += text.charAt(i);
        i++;
        if (i >= text.length) clearInterval(timer);
    }, speed);
}

// AJAX Form Submission
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector('.summary-form');
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Validate form before submission
            const isAuthenticated = document.getElementById('title') !== null;
            const inputType = document.querySelector('input[name="inputType"]:checked').value;

            // Validate title if user is authenticated
            if (isAuthenticated) {
                const title = document.getElementById('title').value.trim();
                if (!title) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error',
                        text: 'Please enter a project title',
                        confirmButtonColor: '#6c5ce7'
                    });
                    return;
                }
            }

            // Validate input based on type
            if (inputType === 'text') {
                const textInput = document.getElementById('textS').value.trim();
                if (!textInput) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error',
                        text: 'Please enter or paste some text to summarize',
                        confirmButtonColor: '#6c5ce7'
                    });
                    return;
                }
                if (textInput.length < 50) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error',
                        text: 'Text must be at least 50 characters long',
                        confirmButtonColor: '#6c5ce7'
                    });
                    return;
                }
            } else if (inputType === 'pdf') {
                const pdfInput = document.querySelector('input[name="pdf_file"]');
                if (!pdfInput.files || pdfInput.files.length === 0) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error',
                        text: 'Please select a PDF file to summarize',
                        confirmButtonColor: '#6c5ce7'
                    });
                    return;
                }

                // Validate file type
                const file = pdfInput.files[0];
                if (!file.name.toLowerCase().endsWith('.pdf')) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Validation Error',
                        text: 'Please select a valid PDF file',
                        confirmButtonColor: '#6c5ce7'
                    });
                    return;
                }
            }

            // If validation passes, proceed with AJAX submission
            window.showLoading();

            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: data.error,
                            confirmButtonColor: '#6c5ce7'
                        });
                        window.hideLoading();
                    } else if (data.task_id) {
                        checkSummaryStatus(data.task_id);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'An unexpected error occurred',
                        confirmButtonColor: '#6c5ce7'
                    });
                    window.hideLoading();
                });
        });
    }

    function checkSummaryStatus(taskId) {
        const interval = setInterval(() => {
            console.log("Checking status for task:", taskId);
            fetch(`/summary/status/${taskId}`)
                .then(r => r.json())
                .then(data => {
                    console.log("Status check response:", data);
                    const status = (data.task_status || "").toUpperCase();

                    if (status === 'SUCCESS') {
                        clearInterval(interval);
                        window.hideLoading();
                        console.log("Task SUCCESS! Result:", data.task_result);
                        console.log("Result type:", typeof data.task_result);
                        console.log("Result is object:", data.task_result instanceof Object);
                        console.log("Result.status:", data.task_result?.status);
                        console.log("Result.summary_abs:", data.task_result?.summary_abs?.substring(0, 50));
                        console.log("Result.summary_ext:", data.task_result?.summary_ext?.substring(0, 50));

                        if (data.task_result && data.task_result.status === 'success') {
                            const summaryDiv = document.getElementById('summary');
                            const absText = document.getElementById('abs_t');
                            const extText = document.getElementById('ext_t');

                            console.log("DOM elements found:", { summaryDiv: !!summaryDiv, absText: !!absText, extText: !!extText });

                            if (summaryDiv) {
                                summaryDiv.style.display = 'block';
                                if (absText) {
                                    absText.innerText = ""; // Clear existing
                                    typeWriter(absText, data.task_result.summary_abs);
                                }
                                if (extText) {
                                    extText.innerText = "";
                                    typeWriter(extText, data.task_result.summary_ext);
                                }
                            } else {
                                console.warn("Summary div not found, reloading page...");
                                location.reload();
                            }
                        } else {
                            const errorMsg = data.task_result ? data.task_result.message : "Result is null (Check task_ignore_result config)";
                            console.error("Task logic error:", errorMsg);
                            console.error("Expected data.task_result.status === 'success', but got:", data.task_result);
                            alert('Processing Error: ' + errorMsg);
                        }
                    } else if (status === 'FAILURE') {
                        clearInterval(interval);
                        window.hideLoading();
                        console.error("Task failed on server:", data);
                        alert('Summarization failed on server.');
                    }
                })
                .catch(err => {
                    clearInterval(interval);
                    window.hideLoading();
                    console.error("Polling error:", err);
                });
        }, 2000);
    }

    // Initial check for content (if page loaded with content from server)
    const abs_t = document.getElementById('abs_t');
    const ext_t = document.getElementById('ext_t');
    if (abs_t && abs_t.innerText.trim().length > 0) {
        // Only type if it looks like fresh content? Or just leave as is. 
        // Existing logic used to type on load.
    }
});
