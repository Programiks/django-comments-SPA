// Initialize comment form validation and HTML toolbar when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#comment-form');

    if (!form) {
        return;
    }

    const textInput = form.querySelector('#id_text');
    const attachmentInput = form.querySelector('#id_attachment');
    const errorContainer = form.querySelector('#client-form-errors');
    const previewButton = form.querySelector('#preview-button');
    const previewContainer = document.querySelector('#comment-preview');

    const MIN_TEXT_LENGTH = 2;
    const MAX_TEXT_LENGTH = 2000;
    const MAX_TEXT_FILE_SIZE = 100 * 1024;

    /**
     * Display a list of validation error messages in the form.
     * @param {string[]} messages - Array of error messages to show.
     */
    function showErrors(messages) {
        errorContainer.innerHTML = '';

        if (messages.length === 0) {
            errorContainer.hidden = true;
            return;
        }

        const list = document.createElement('ul');

        messages.forEach((message) => {
            const item = document.createElement('li');
            item.textContent = message;
            list.appendChild(item);
        });

        errorContainer.appendChild(list);
        errorContainer.hidden = false;
    }

    /**
     * Validate comment text length and return an error message if invalid.
     * @returns {string|null} Error message if validation fails, otherwise null.
     */
    function validateText() {
        const text = textInput.value.trim();

        if (text.length < MIN_TEXT_LENGTH || text.length > MAX_TEXT_LENGTH) {
            return `Comment text must be between ${MIN_TEXT_LENGTH} and ${MAX_TEXT_LENGTH} characters.`;
        }

        return null;
    }

    /**
     * Validate attachment type and size, return an error message if invalid.
     * @returns {string|null} Error message if validation fails, otherwise null.
     */
    function validateAttachment() {
        const file = attachmentInput.files[0];

        if (!file) {
            return null;
        }

        const allowedImageTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const isImage = allowedImageTypes.includes(file.type);
        const isTextFile = file.type === 'text/plain'
            || file.name.toLowerCase().endsWith('.txt');

        if (!isImage && !isTextFile) {
            return 'Only JPG, PNG, GIF images or TXT files are allowed.';
        }

        if (isTextFile && file.size > MAX_TEXT_FILE_SIZE) {
            return 'TXT file size cannot exceed 100 KB.';
        }

        return null;
    }

    /**
     * Run all validations and show errors if any.
     * @returns {boolean} True if the form is valid, otherwise false.
     */
    function validateForm() {
        const errors = [];

        const textError = validateText();
        const attachmentError = validateAttachment();

        if (textError) {
            errors.push(textError);
        }

        if (attachmentError) {
            errors.push(attachmentError);
        }

        showErrors(errors);
        return errors.length === 0;
    }

    /**
     * Send text to the server and render a preview without reloading the page.
     */
    async function showPreview() {
        const text = textInput.value;

        // Basic validation before sending
        const textError = validateText();
        if (textError) {
            showErrors([textError]);
            if (previewContainer) {
                previewContainer.hidden = true;
                previewContainer.textContent = '';
            }
            return;
        }

        if (!previewContainer) {
            return;
        }

        // Get CSRF token from the hidden input in the form
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

        try {
            const response = await fetch('/comments/preview/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: `text=${encodeURIComponent(text)}`
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            if (data.preview_html) {
                previewContainer.innerHTML = data.preview_html;
                previewContainer.hidden = false;
            } else {
                previewContainer.hidden = true;
                previewContainer.textContent = '';
            }
        } catch (error) {
            // On error, hide preview
            previewContainer.hidden = true;
            previewContainer.textContent = '';
        }
    }

    // Prevent form submission if validation fails
    form.addEventListener('submit', (event) => {
        if (!validateForm()) {
            event.preventDefault();
        }
    });

    // Revalidate on text input and attachment change
    textInput.addEventListener('input', validateForm);
    attachmentInput.addEventListener('change', validateForm);

    // Preview button handler
    if (previewButton) {
        previewButton.addEventListener('click', showPreview);
    }

    const toolbarButtons = form.querySelectorAll('.html-toolbar button');

    /**
     * Wrap selected text with opening and closing HTML tags.
     * @param {string} tagName - HTML tag name to wrap the selection (e.g., 'strong', 'i', 'code').
     */
    function wrapSelection(tagName) {
        const selectedText = textInput.value.substring(
            textInput.selectionStart,
            textInput.selectionEnd
        );
        const openingTag = `<${tagName}>`;
        const closingTag = `</${tagName}>`;

        textInput.setRangeText(
            `${openingTag}${selectedText}${closingTag}`,
            textInput.selectionStart,
            textInput.selectionEnd,
            'end'
        );

        textInput.focus();

        if (formWasSubmitted) {
            validateAndShowErrors();
        }
    }

    /**
     * Handle toolbar button clicks to insert HTML tags.
     * For 'a' tags, prompts the user for a URL and inserts a complete anchor element.
     */
    toolbarButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const tagName = button.dataset.tag;

            if (tagName === 'a') {
                const href = window.prompt('Enter the URL for the link:');

                if (href === null || href.trim() === '') {
                    return;
                }

                const selectedText = textInput.value.substring(
                    textInput.selectionStart,
                    textInput.selectionEnd
                );

                textInput.setRangeText(
                    `<a href="${href.trim()}">${selectedText}</a>`,
                    textInput.selectionStart,
                    textInput.selectionEnd,
                    'end'
                );

                textInput.focus();

                if (formWasSubmitted) {
                    validateAndShowErrors();
                }

                return;
            }

            wrapSelection(tagName);
        });
    });

});