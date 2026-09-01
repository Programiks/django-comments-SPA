const { createApp } = Vue;

createApp({
    data() {
        return {
            form: {
                author_name: '',
                email: '',
                home_page: '',
                text: '',
                attachment: null,
                captcha: ''
            },
            errors: [],
            previewHtml: '',
            showPreviewContainer: false
        };
    },

    methods: {
        insertTag(tag) {
            const textarea = document.getElementById('id_text');

            if (!textarea) {
                return;
            }

            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const value = this.form.text;

            const before = value.slice(0, start);
            let selected = value.slice(start, end);
            const after = value.slice(end);

            if (tag === 'a') {
                const url = window.prompt('Enter URL:', 'https://');

                if (!url || !url.trim()) {
                    return;
                }

                selected = `<a href="${url.trim()}">${selected || 'link'}</a>`;
            } else {
                selected = `<${tag}>${selected}</${tag}>`;
            }

            this.form.text = before + selected + after;

            this.$nextTick(() => {
                textarea.focus();

                const cursorPosition = start + selected.length;
                textarea.setSelectionRange(cursorPosition, cursorPosition);
            });
        },

        handleAttachmentChange(event) {
            this.form.attachment = event.target.files[0] || null;
            this.validateForm();
        },

        validateAuthorName() {
            const name = this.form.author_name.trim();

            if (!name) {
                return 'User Name is required.';
            }

            const validPattern = /^[A-Za-z0-9]+$/;

            if (!validPattern.test(name)) {
                return 'User Name must contain only Latin letters and digits.';
            }

            return null;
        },

        validateEmail() {
            const email = this.form.email.trim();

            if (!email) {
                return 'E-mail is required.';
            }

            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!emailPattern.test(email)) {
                return 'E-mail must be a valid email address.';
            }

            return null;
        },

        validateHomePage() {
            const url = this.form.home_page.trim();

            if (!url) {
                return null;
            }

            const urlPattern = /^https?:\/\/[^\s]+$/i;

            if (!urlPattern.test(url)) {
                return 'Home page must be a valid URL (http:// or https://).';
            }

            return null;
        },

        validateCaptcha() {
            const captcha = this.form.captcha.trim();

            if (!captcha) {
                return 'CAPTCHA is required.';
            }

            return null;
        },

        validateTextTags() {
            const text = this.form.text;

            if (!text) {
                return null;
            }

            const tagRegex = /<\/?([a-z][a-z0-9]*)\b[^>]*>/gi;
            const matches = text.match(tagRegex) || [];

            const allowedTags = ['a', 'code', 'i', 'strong'];
            const stack = [];

            for (const tagFull of matches) {
                const tagMatch = tagFull.match(/^<\/?([a-z][a-z0-9]*)/i);
                if (!tagMatch) {
                    return 'Invalid tag detected.';
                }

                const tagName = tagMatch[1].toLowerCase();

                if (!allowedTags.includes(tagName)) {
                    return `Tag <${tagName}> is not allowed. Allowed tags: a, code, i, strong.`;
                }

                const isClosing = tagFull.startsWith('</');

                if (!isClosing) {
                    stack.push(tagName);
                } else {
                    if (stack.length === 0) {
                        return 'Closing tag without matching opening tag.';
                    }

                    const lastOpen = stack.pop();
                    if (lastOpen !== tagName) {
                        return `Mismatched tag: expected </${lastOpen}>, got ${tagFull}.`;
                    }
                }
            }

            if (stack.length > 0) {
                return `Unclosed tag: <${stack[stack.length - 1]}>.`;
            }

            return null;
        },

        validateText() {
            const text = this.form.text.trim();

            if (text.length < 2 || text.length > 2000) {
                return 'Comment text must be between 2 and 2000 characters.';
            }

            return null;
        },

        validateAttachment() {
            const file = this.form.attachment;

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

            if (isTextFile && file.size > 100 * 1024) {
                return 'TXT file size cannot exceed 100 KB.';
            }

            return null;
        },

        validateForm() {
            const errors = [];

            const authorNameError = this.validateAuthorName();
            const emailError = this.validateEmail();
            const homePageError = this.validateHomePage();
            const captchaError = this.validateCaptcha();
            const textLengthError = this.validateText();
            const textTagsError = this.validateTextTags();
            const attachmentError = this.validateAttachment();

            if (authorNameError) {
                errors.push(authorNameError);
            }

            if (emailError) {
                errors.push(emailError);
            }

            if (homePageError) {
                errors.push(homePageError);
            }

            if (captchaError) {
                errors.push(captchaError);
            }

            if (textLengthError) {
                errors.push(textLengthError);
            }

            if (textTagsError) {
                errors.push(textTagsError);
            }

            if (attachmentError) {
                errors.push(attachmentError);
            }

            this.errors = errors;

            return errors.length === 0;
        },

        handleSubmit(event) {
            if (!this.validateForm()) {
                event.preventDefault();
            }
        },

        async showPreview() {
            if (!this.validateForm()) {
                this.previewHtml = '';
                this.showPreviewContainer = false;
                return;
            }

            try {
                const response = await fetch('/comments/preview/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: `text=${encodeURIComponent(this.form.text)}`
                });

                if (!response.ok) {
                    throw new Error('Preview request failed.');
                }

                const data = await response.json();

                if (data.preview_html) {
                    this.previewHtml = data.preview_html;
                    this.showPreviewContainer = true;
                    return;
                }

                this.previewHtml = '';
                this.showPreviewContainer = false;
            } catch (error) {
                this.previewHtml = '';
                this.showPreviewContainer = false;
                this.errors = [
                    'Could not generate preview. Please try again.'
                ];
            }
        }
    }
}).mount('#vue-app');