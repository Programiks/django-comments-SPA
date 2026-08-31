document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#comment-form');

    if (!form) {
        return;
    }

    const textInput = form.querySelector('#id_text');
    const attachmentInput = form.querySelector('#id_attachment');
    const errorContainer = form.querySelector('#client-form-errors');

    const MIN_TEXT_LENGTH = 2;
    const MAX_TEXT_LENGTH = 2000;
    const MAX_TEXT_FILE_SIZE = 100 * 1024;

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

    function validateText() {
        const text = textInput.value.trim();

        if (text.length < MIN_TEXT_LENGTH || text.length > MAX_TEXT_LENGTH) {
            return `Текст коментаря має містити від ${MIN_TEXT_LENGTH} до ${MAX_TEXT_LENGTH} символів.`;
        }

        return null;
    }

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
            return 'Можна додати лише зображення JPG, PNG, GIF або текстовий файл TXT.';
        }

        if (isTextFile && file.size > MAX_TEXT_FILE_SIZE) {
            return 'Розмір TXT-файлу не може перевищувати 100 КБ.';
        }

        return null;
    }

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

    form.addEventListener('submit', (event) => {
        if (!validateForm()) {
            event.preventDefault();
        }
    });

    textInput.addEventListener('input', validateForm);
    attachmentInput.addEventListener('change', validateForm);
});