/**
 * Markdown Rendering Module
 * Handles Markdown to HTML conversion with code highlighting
 */

class MarkdownRenderer {
    constructor() {
        // Configure marked
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                highlight: (code, lang) => {
                    if (lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (err) {
                            console.error('Highlight error:', err);
                        }
                    }
                    return hljs.highlightAuto(code).value;
                }
            });
        }
    }

    /**
     * Render markdown to HTML
     * @param {string} markdown - Markdown text
     * @returns {string} Sanitized HTML
     */
    render(markdown) {
        if (!markdown) return '';

        try {
            // Convert markdown to HTML
            const html = marked.parse(markdown);

            // Sanitize HTML to prevent XSS
            if (typeof DOMPurify !== 'undefined') {
                return DOMPurify.sanitize(html, {
                    ADD_ATTR: ['target'], // Allow target attribute for links
                    ADD_TAGS: ['iframe'] // Allow iframes if needed
                });
            }

            return html;
        } catch (error) {
            console.error('Markdown rendering error:', error);
            return this.escapeHtml(markdown);
        }
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Extract code blocks from markdown
     * @param {string} markdown - Markdown text
     * @returns {Array} Array of code blocks
     */
    extractCodeBlocks(markdown) {
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        const blocks = [];
        let match;

        while ((match = codeBlockRegex.exec(markdown)) !== null) {
            blocks.push({
                language: match[1] || 'plaintext',
                code: match[2].trim()
            });
        }

        return blocks;
    }

    /**
     * Typewriter effect for text
     * @param {HTMLElement} element - Target element
     * @param {string} text - Text to type
     * @param {number} speed - Typing speed in ms
     * @returns {Promise} Resolves when typing is complete
     */
    async typewriter(element, text, speed = 20) {
        return new Promise((resolve) => {
            let i = 0;
            const timer = setInterval(() => {
                if (i < text.length) {
                    element.innerHTML += text.charAt(i);
                    i++;
                    // Auto-scroll
                    element.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                } else {
                    clearInterval(timer);
                    resolve();
                }
            }, speed);
        });
    }
}

// Export singleton instance
const markdownRenderer = new MarkdownRenderer();
