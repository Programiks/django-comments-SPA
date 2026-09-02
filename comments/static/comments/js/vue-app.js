/**
 * Vue 3 application for the comment system.
 *
 * This module provides the frontend logic for:
 * - User authentication (login/register/logout)
 * - Comment form validation and submission
 * - CAPTCHA handling
 * - Live comment preview
 * - Real-time updates via WebSocket
 * - File attachment validation
 *
 * @module comments/vue-app
 */

const { createApp } = Vue;

createApp({
    /**
     * Reactive data properties for the comment application.
     *
     * @returns {Object} Application state including auth, form data, and UI flags.
     */
    data() {
        return {
            // Auth state (single modal)
            isLoggedIn: false,
            accessToken: null,

            showAuthModal: false,
            isLoginMode: true,

            authForm: {
                username: '',
                password: '',
                passwordConfirm: '',
                email: '',
            },

            // Comment form
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
            showPreviewContainer: false,
            socket: null,
            isSubmittingComment: false,
            // Unique token for CAPTCHA session tracking
            captchaToken: `${Date.now()}-${Math.random().toString(16).slice(2)}`
        };
    },

    /**
     * Computed properties for derived state.
     */
    computed: {
        /**
         * Check if form is valid and ready for submission.
         *
         * @returns {boolean} True if no errors and required fields are filled.
         */
        canSubmit() {
            return this.errors.length === 0
                && this.form.author_name.trim()
                && this.form.email.trim()
                && this.form.text.trim().length >= 2;
        },

        /**
         * Generate CAPTCHA image URL with current token.
         *
         * @returns {string} URL to fetch CAPTCHA image.
         */
        captchaImageUrl() {
            return `/comments/captcha/?token=${encodeURIComponent(this.captchaToken)}`;
        }
    },

    /**
     * Lifecycle hook: called after component instance is created.
     * Initializes auth state from localStorage and connects WebSocket.
     */
    created() {
        this.loadAuthFromStorage();
        this.connectWebSocket();
    },

    /**
     * Component methods for authentication, validation, and comment handling.
     */
    methods: {
        /**
         * Establish WebSocket connection for real-time comment notifications.
         *
         * Uses wss:// for HTTPS and ws:// for HTTP connections.
         * Reloads page when new comment notification is received.
         */
        connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

            this.socket = new WebSocket(
                `${protocol}://${window.location.host}/ws/comments/`
            );

            this.socket.onopen = () => {};
            this.socket.onerror = () => {};

            this.socket.onmessage = (event) => {
                if (event.data === 'new_comment') {
                    window.location.reload();
                }
            };
        },

        // ---------- Auth methods ----------

        /**
         * Load authentication state from localStorage.
         *
         * Restores access token, username, and email from previous session.
         * Pre-fills comment form with stored user data if available.
         */
        loadAuthFromStorage() {
            const token = localStorage.getItem('access_token');
            const username = localStorage.getItem('current_username');
            const email = localStorage.getItem('current_email');

            if (token) {
                this.accessToken = token;
                this.isLoggedIn = true;
            }

            if (username) {
                this.currentUsername = username;
                this.form.author_name = username;
            }

            if (email) {
                this.form.email = email;
            }
        },

        /**
         * Save access token and username to localStorage.
         *
         * @param {string} token - JWT access token from authentication response.
         */
        saveToken(token) {
            this.accessToken = token;
            this.isLoggedIn = true;
            localStorage.setItem('access_token', token);

            if (this.currentUsername) {
                localStorage.setItem('current_username', this.currentUsername);
            }
        },

        /**
         * Clear authentication state and remove tokens from localStorage.
         */
        clearToken() {
            this.accessToken = null;
            this.isLoggedIn = false;
            this.currentUsername = '';
            localStorage.removeItem('access_token');
            localStorage.removeItem('current_username');
            localStorage.removeItem('current_email');
        },

        /**
         * Open authentication modal in login mode.
         *
         * Resets auth form to initial state.
         */
        openLoginModal() {
            this.isLoginMode = true;
            this.authForm = {
                username: '',
                password: '',
                passwordConfirm: '',
                email: '',
            };
            this.showAuthModal = true;
        },

        /**
         * Close authentication modal.
         */
        closeAuthModal() {
            this.showAuthModal = false;
        },

        /**
         * Switch modal to registration mode.
         */
        switchToRegister() {
            this.isLoginMode = false;
            this.authForm.passwordConfirm = '';
        },

        /**
         * Switch modal to login mode.
         */
        switchToLogin() {
            this.isLoginMode = true;
        },

        /**
         * Handle authentication form submission (login or register).
         *
         * @async
         */
        async handleAuthSubmit() {
            if (!this.isLoginMode) {
                await this.register();
                return;
            }

            await this.login();
        },

        /**
         * Authenticate user with username and password.
         *
         * Sends POST request to /api/auth/login/ and stores JWT token on success.
         * Pre-fills comment form with user data from response.
         *
         * @async
         */
        async login() {
            if (!this.authForm.username || !this.authForm.password) {
                alert('Username and password are required.');
                return;
            }

            try {
                const response = await fetch('/api/auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: this.authForm.username,
                        password: this.authForm.password
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || 'Login failed.');
                }

                const data = await response.json();

                this.currentUsername = data.username || this.authForm.username;
                this.saveToken(data.access);

                localStorage.setItem('current_username', data.username || this.authForm.username);
                localStorage.setItem('current_email', data.email || '');

                this.form.author_name = data.username || this.authForm.username;
                this.form.email = data.email || '';

                this.authForm.username = '';
                this.authForm.password = '';
                this.showAuthModal = false;
            } catch (error) {
                alert(error.message || 'Login failed.');
            }
        },

        /**
         * Register new user and authenticate.
         *
         * Validates password match, sends POST to /api/auth/register/,
         * then automatically logs in the user.
         *
         * @async
         */
        async register() {
            if (!this.authForm.username || !this.authForm.password) {
                alert('Username and password are required.');
                return;
            }

            if (!this.authForm.email) {
                alert('Email is required.');
                return;
            }

            if (this.authForm.password !== this.authForm.passwordConfirm) {
                alert('Passwords do not match.');
                return;
            }

            try {
                const response = await fetch('/api/auth/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: this.authForm.username,
                        email: this.authForm.email,
                        password: this.authForm.password
                    })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || 'Registration failed.');
                }

                // Auto-login after successful registration
                const loginResponse = await fetch('/api/auth/login/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: this.authForm.username,
                        password: this.authForm.password
                    })
                });

                if (!loginResponse.ok) {
                    throw new Error('Registration succeeded, but login failed.');
                }

                const loginData = await loginResponse.json();
                this.currentUsername = this.authForm.username;
                this.saveToken(loginData.access);

                localStorage.setItem('current_username', this.authForm.username);
                localStorage.setItem('current_email', this.authForm.email || '');

                this.form.author_name = this.authForm.username;
                this.form.email = this.authForm.email || '';

                this.authForm.username = '';
                this.authForm.email = '';
                this.authForm.password = '';
                this.authForm.passwordConfirm = '';
                this.showAuthModal = false;
            } catch (error) {
                alert(error.message || 'Registration failed.');
            }
        },

        /**
         * Logout user and clear authentication state.
         *
         * Resets form fields to empty state.
         */
        logout() {
            this.clearToken();
            this.form.author_name = '';
            this.form.email = '';
        },

        // ---------- Comment methods ----------

        /**
         * Insert HTML tag at cursor position in comment textarea.
         *
         * For <a> tags, prompts user for URL.
         * For other tags, wraps selected text.
         *
         * @param {string} tag - Tag name to insert (e.g., 'strong', 'code', 'a').
         */
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

        /**
         * Handle file attachment input change.
         *
         * @param {Event} event - File input change event.
         */
        handleAttachmentChange(event) {
            this.form.attachment = event.target.files[0] || null;
            this.validateForm();
        },

        /**
         * Validate author name field.
         *
         * @returns {string|null} Error message or null if valid.
         */
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

        /**
         * Validate email field.
         *
         * @returns {string|null} Error message or null if valid.
         */
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

        /**
         * Validate home page URL field.
         *
         * @returns {string|null} Error message or null if valid/empty.
         */
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

        /**
         * Validate CAPTCHA field.
         *
         * @returns {string|null} Error message or null if valid.
         */
        validateCaptcha() {
            const captcha = this.form.captcha.trim();

            if (!captcha) {
                return 'CAPTCHA is required.';
            }

            return null;
        },

        /**
         * Validate HTML tags in comment text.
         *
         * Checks that only allowed tags are used and they are properly nested.
         * Allowed tags: a, code, i, strong.
         *
         * @returns {string|null} Error message or null if valid.
         */
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

        /**
         * Validate comment text length.
         *
         * @returns {string|null} Error message or null if valid.
         */
        validateText() {
            const text = this.form.text.trim();

            if (text.length < 2 || text.length > 2000) {
                return 'Comment text must be between 2 and 2000 characters.';
            }

            return null;
        },

        /**
         * Validate file attachment type and size.
         *
         * Allowed: JPG, PNG, GIF images; TXT files (max 100 KB).
         *
         * @returns {string|null} Error message or null if valid/no attachment.
         */
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

        /**
         * Run all form validations and populate errors array.
         *
         * @returns {boolean} True if no validation errors.
         */
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

        /**
         * Clear attachment file and reset file input.
         */
        clearAttachment() {
            this.form.attachment = null;

            const fileInput = document.getElementById('id_attachment');
            if (fileInput) {
                fileInput.value = '';
            }
        },

        /**
         * Handle comment form submission.
         *
         * Validates form, sends AJAX POST request, and reloads page on success.
         * Requires login for file attachments.
         *
         * @async
         * @param {Event} event - Form submit event.
         */
        async handleSubmit(event) {
            event.preventDefault();

            this.isSubmittingComment = true;
            this.errors = [];

            if (!this.isLoggedIn && this.form.attachment) {
                alert('Please log in or register to upload images.');
                this.form.attachment = null;

                const fileInput = document.getElementById('id_attachment');
                if (fileInput) {
                    fileInput.value = '';
                }

                this.isSubmittingComment = false;
                return;
            }

            if (!this.validateForm()) {
                this.isSubmittingComment = false;
                return;
            }

            const formData = new FormData();
            formData.append('author_name', this.form.author_name);
            formData.append('email', this.form.email);
            formData.append('home_page', this.form.home_page || '');
            formData.append('text', this.form.text);
            formData.append('captcha', this.form.captcha);
            formData.append('captcha_token', this.captchaToken);

            if (this.form.attachment) {
                formData.append('attachment', this.form.attachment);
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken || '',
                    },
                    body: formData,
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    this.errors = errorData.errors || ['Could not submit comment. Please try again.'];
                    throw new Error('Submit failed.');
                }

                // Reset form on success
                this.form.author_name = '';
                this.form.email = '';
                this.form.home_page = '';
                this.form.text = '';
                this.form.captcha = '';
                this.form.attachment = null;

                const fileInput = document.getElementById('id_attachment');
                if (fileInput) {
                    fileInput.value = '';
                }

                this.errors = [];
                this.showPreviewContainer = false;
                this.previewHtml = '';

                // Reload to show the new comment; other tabs will reload via WebSocket
                window.location.reload();
            } catch (error) {
                this.errors = ['Could not submit comment. Please try again.'];
            } finally {
                this.isSubmittingComment = false;
            }
        },

        /**
         * Generate and display sanitized HTML preview of comment text.
         *
         * Sends POST request to /comments/preview/ endpoint.
         *
         * @async
         */
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
