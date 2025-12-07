/**
 * Markdown 渲染工具
 */
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import 'highlight.js/styles/atom-one-light.css';

// 创建 Markdown 实例
const md = new MarkdownIt({
  html: false, // 不允许 HTML 标签
  linkify: true, // 自动识别链接
  typographer: true, // 排版优化
  breaks: true, // 换行转 <br>
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="code-block"><div class="code-header"><span class="code-lang">${lang}</span><button class="code-copy-btn" onclick="copyCode(this)">复制</button></div><code class="hljs language-${lang}">${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`;
      } catch (__) {
        // ignore
      }
    }
    return `<pre class="code-block"><code class="hljs">${md.utils.escapeHtml(str)}</code></pre>`;
  },
});

/**
 * 渲染 Markdown
 */
export const renderMarkdown = (content: string): string => {
  return md.render(content);
};

/**
 * 复制代码块
 */
export const copyCode = (button: HTMLButtonElement) => {
  const pre = button.closest('pre');
  if (!pre) return;
  
  const code = pre.querySelector('code');
  if (!code) return;
  
  const text = code.textContent || '';
  
  navigator.clipboard.writeText(text).then(() => {
    const originalText = button.textContent;
    button.textContent = '已复制!';
    button.classList.add('copied');
    
    setTimeout(() => {
      button.textContent = originalText;
      button.classList.remove('copied');
    }, 2000);
  }).catch((err) => {
    console.error('复制失败:', err);
  });
};

// 暴露全局函数（用于 onclick）
(window as any).copyCode = copyCode;

export default { renderMarkdown, copyCode };

