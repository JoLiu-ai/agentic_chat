/**
 * Main Application Logic - Redesigned
 * Handles UI interactions and Chat functionality with time-based grouping
 */

class AgenticChatApp {
    constructor() {
        this.currentSessionId = null;
        this.sessions = [];
        this.isLoading = false;
        this.thinkMode = true; // Default to think mode
        this.messageVersions = new Map(); // Track message versions {messageId: [{content, timestamp, agent}]}

        this.initializeElements();
        this.attachEventListeners();
        this.initContextMenu(); // Initialize context menu
        this.loadSessions();
    }

    initializeElements() {
        // UI Elements
        this.menuToggle = document.getElementById('menuToggle');
        this.sidebar = document.getElementById('sidebar');
        this.newChatButton = document.getElementById('newChatButton');
        this.sessionSearch = document.getElementById('sessionSearch');
        this.modelSelect = document.getElementById('modelSelect');
        this.modeToggle = document.getElementById('modeToggle');
        this.modeIcon = document.getElementById('modeIcon');
        this.modeText = document.getElementById('modeText');

        // Time group containers
        this.starredGroup = document.getElementById('starredGroup');
        this.todayGroup = document.getElementById('todayGroup');
        this.yesterdayGroup = document.getElementById('yesterdayGroup');
        this.lastWeekGroup = document.getElementById('lastWeekGroup');
        this.earlierGroup = document.getElementById('earlierGroup');
        this.sidebarEmpty = document.getElementById('sidebarEmpty');

        // Time group lists
        this.starredList = document.getElementById('starredList');
        this.todayList = document.getElementById('todayList');
        this.yesterdayList = document.getElementById('yesterdayList');
        this.lastWeekList = document.getElementById('lastWeekList');
        this.earlierList = document.getElementById('earlierList');

        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.loadingIndicator = document.getElementById('loadingIndicator');
    }

    attachEventListeners() {
        // Menu toggle (mobile)
        this.menuToggle?.addEventListener('click', () => {
            this.sidebar.classList.toggle('open');
        });

        // New chat button
        this.newChatButton.addEventListener('click', () => this.startNewChat());

        // Example prompts
        document.querySelectorAll('.example-prompt').forEach(button => {
            button.addEventListener('click', () => {
                this.messageInput.value = button.textContent;
                this.sendMessage();
            });
        });

        // Message input
        this.messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
            this.sendButton.disabled = !this.messageInput.value.trim();
        });

        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (this.messageInput.value.trim()) {
                    this.sendMessage();
                }
            }
        });

        // Send button
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Session search
        this.sessionSearch.addEventListener('input', (e) => {
            this.filterSessions(e.target.value);
        });

        // Model selector
        this.modelSelect.addEventListener('change', (e) => {
            apiClient.setModel(e.target.value);
        });

        // Mode toggle
        this.modeToggle.addEventListener('click', () => {
            this.toggleThinkMode();
        });
    }

    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
    }

    startNewChat() {
        this.currentSessionId = apiClient.generateSessionId();
        this.welcomeScreen.style.display = 'none';
        this.chatMessages.style.display = 'block';
        this.chatMessages.innerHTML = '';
        this.messageInput.focus();

        // Close sidebar on mobile
        this.sidebar.classList.remove('open');
    }

    async loadSessions() {
        try {
            const data = await apiClient.getSessions();
            this.sessions = data.sessions || [];
            this.renderSessionsByTime();
        } catch (error) {
            console.error('Error loading sessions:', error);
            this.sessions = [];
            this.sidebarEmpty.style.display = 'block';
        }
    }

    renderSessionsByTime() {
        if (this.sessions.length === 0) {
            this.sidebarEmpty.style.display = 'block';
            this.hideAllGroups();
            return;
        }

        this.sidebarEmpty.style.display = 'none';

        // Group sessions by time
        const groups = this.groupSessionsByTime(this.sessions);

        // Render each group
        this.renderGroup(this.starredGroup, this.starredList, groups.starred, '⭐');
        this.renderGroup(this.todayGroup, this.todayList, groups.today, '💬');
        this.renderGroup(this.yesterdayGroup, this.yesterdayList, groups.yesterday, '💬');
        this.renderGroup(this.lastWeekGroup, this.lastWeekList, groups.lastWeek, '💬');
        this.renderGroup(this.earlierGroup, this.earlierList, groups.earlier, '💬');
    }

    groupSessionsByTime(sessions) {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        const lastWeek = new Date(today);
        lastWeek.setDate(lastWeek.getDate() - 7);

        const groups = {
            starred: [],
            today: [],
            yesterday: [],
            lastWeek: [],
            earlier: []
        };

        sessions.forEach(session => {
            const sessionDate = new Date(session.created_at);

            if (session.is_starred) {
                groups.starred.push(session);
            } else if (sessionDate >= today) {
                groups.today.push(session);
            } else if (sessionDate >= yesterday) {
                groups.yesterday.push(session);
            } else if (sessionDate >= lastWeek) {
                groups.lastWeek.push(session);
            } else {
                groups.earlier.push(session);
            }
        });

        return groups;
    }

    renderGroup(groupElement, listElement, sessions, icon) {
        if (sessions.length === 0) {
            groupElement.style.display = 'none';
            return;
        }

        groupElement.style.display = 'block';
        listElement.innerHTML = sessions.map(session =>
            this.createSessionItemHTML(session, icon)
        ).join('');

        this.attachSessionItemListeners(listElement);
    }

    createSessionItemHTML(session, icon) {
        return `
            <div class="session-item-new ${session.session_id === this.currentSessionId ? 'active' : ''}"
                 data-session-id="${session.session_id}"
                 data-title="${session.title}"
                 data-starred="${session.is_starred}">
                <span class="session-icon">${icon}</span>
                <span class="session-title-new">${session.title || '未命名对话'}</span>
                <!-- Context menu trigger (three dots) could go here if needed, but we use right click -->
                <button class="session-more-btn" title="更多操作">⋯</button>
            </div>
        `;
    }

    attachSessionItemListeners(container) {
        container.querySelectorAll('.session-item-new').forEach(item => {
            // Left click to load session
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.session-more-btn')) {
                    this.loadSession(item.dataset.sessionId);
                }
            });

            // Right click for context menu
            item.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.showContextMenu(e, item.dataset.sessionId);
            });

            // More button click (optional fallback)
            const moreBtn = item.querySelector('.session-more-btn');
            if (moreBtn) {
                moreBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.showContextMenu(e, item.dataset.sessionId);
                });
            }
        });
    }

    showContextMenu(e, sessionId) {
        const menu = document.getElementById('contextMenu');
        this.contextMenuSessionId = sessionId;

        // Position menu
        const x = e.clientX;
        const y = e.clientY;

        menu.style.left = `${x}px`;
        menu.style.top = `${y}px`;
        menu.classList.add('visible');

        // Update Star text based on state
        const session = this.sessions.find(s => s.session_id === sessionId);
        const starText = menu.querySelector('[data-action="star"] span');
        if (session && starText) {
            starText.textContent = session.is_starred ? 'Unstar' : 'Star';
        }
    }

    initContextMenu() {
        const menu = document.getElementById('contextMenu');

        // Hide menu on click elsewhere
        document.addEventListener('click', () => {
            menu.classList.remove('visible');
        });

        // Menu item clicks
        menu.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', () => {
                const action = item.dataset.action;
                const sessionId = this.contextMenuSessionId;

                if (!sessionId) return;

                switch (action) {
                    case 'star':
                        const session = this.sessions.find(s => s.session_id === sessionId);
                        if (session) {
                            this.toggleStar(sessionId, !session.is_starred);
                        }
                        break;
                    case 'rename':
                        this.renameSession(sessionId);
                        break;
                    case 'delete':
                        this.deleteSession(sessionId);
                        break;
                    case 'add-to-project':
                        alert('Add to project feature coming soon!');
                        break;
                }
                menu.classList.remove('visible');
            });
        });
    }

    async renameSession(sessionId) {
        const sessionFn = this.sessions.find(s => s.session_id === sessionId);
        const newTitle = prompt("Enter new title:", sessionFn ? sessionFn.title : "");

        if (newTitle && newTitle.trim()) {
            try {
                await apiClient.updateSession(sessionId, { title: newTitle.trim() });
                await this.loadSessions();
            } catch (error) {
                console.error('Failed to rename session:', error);
                alert('重命名失败');
            }
        }
    }

    hideAllGroups() {
        this.starredGroup.style.display = 'none';
        this.todayGroup.style.display = 'none';
        this.yesterdayGroup.style.display = 'none';
        this.lastWeekGroup.style.display = 'none';
        this.earlierGroup.style.display = 'none';
    }

    async toggleStar(sessionId, isStarred) {
        try {
            await apiClient.toggleStar(sessionId, isStarred);
            await this.loadSessions();
        } catch (error) {
            console.error('Error toggling star:', error);
        }
    }

    async deleteSession(sessionId) {
        if (!confirm('确定要删除这个对话吗？')) return;

        try {
            await apiClient.deleteSession(sessionId);
            if (sessionId === this.currentSessionId) {
                this.currentSessionId = null;
                this.welcomeScreen.style.display = 'flex';
                this.chatMessages.style.display = 'none';
            }
            await this.loadSessions();
        } catch (error) {
            console.error('Error deleting session:', error);
        }
    }

    async loadSession(sessionId) {
        console.log('🔍 loadSession called with:', sessionId);
        try {
            this.currentSessionId = sessionId;
            this.welcomeScreen.style.display = 'none';
            this.chatMessages.style.display = 'block';
            this.chatMessages.innerHTML = '';

            // Load messages
            console.log('📡 Fetching messages for session:', sessionId);
            const data = await apiClient.getSessionMessages(sessionId);
            const messages = data.messages || [];
            console.log('📨 Received messages:', messages.length);

            if (messages.length === 0) {
                console.log('⚠️ No messages in this session');
                // Show empty state message
                this.chatMessages.innerHTML = '<div style="text-align:center;padding:40px;color:#999;">此会话暂无消息</div>';
            } else {
                messages.forEach(msg => {
                    this.addMessage(msg.content, msg.role, msg.agent_type);
                });
            }

            // Refresh to update active state
            await this.loadSessions();

            // Close sidebar on mobile
            this.sidebar.classList.remove('open');

            // Scroll to bottom
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        } catch (error) {
            console.error('❌ Error loading session:', error);
            alert('加载对话失败，请重试');
        }
    }

    filterSessions(query) {
        const lowerQuery = query.toLowerCase();

        document.querySelectorAll('.session-item-new').forEach(item => {
            const title = item.querySelector('.session-title-new').textContent.toLowerCase();
            item.style.display = title.includes(lowerQuery) ? 'flex' : 'none';
        });
        this.sidebar.classList.remove('open');
    }

    toggleThinkMode() {
        this.thinkMode = !this.thinkMode;

        if (this.thinkMode) {
            this.modeToggle.classList.add('active');
            this.modeIcon.textContent = '💡';
            this.modeText.textContent = 'Think';
        } else {
            this.modeToggle.classList.remove('active');
            this.modeIcon.textContent = '⚡';
            this.modeText.textContent = 'Simple';
        }
    }

    async sendMessage() {
        if (!this.messageInput.value.trim() || this.isLoading) return;

        const message = this.messageInput.value.trim();
        const selectedModel = this.modelSelect.value;

        this.messageInput.value = '';
        this.sendButton.disabled = true;
        this.adjustTextareaHeight();

        if (!this.currentSessionId) {
            this.startNewChat();
        }

        this.addMessage(message, 'user');

        // Show thinking only in Think mode
        if (this.thinkMode) {
            this.showThinking('Assistant');
        }

        try {
            const response = await apiClient.sendMessage(message, this.currentSessionId, selectedModel);

            if (this.thinkMode) {
                this.hideThinking();
            }

            this.addMessage(response.response, 'assistant', response.agent_type);

            // If this is a response after edit, add version history
            if (this.pendingVersionMessageId) {
                const messageId = this.pendingVersionMessageId;
                const versions = this.pendingVersions || [];

                // Add new version
                versions.push({
                    content: response.response,
                    agent: response.agent_type || 'Assistant',
                    timestamp: new Date().toISOString()
                });

                this.messageVersions.set(messageId, versions);

                // Add version navigator if we have multiple versions
                if (versions.length > 1) {
                    const lastMessage = this.chatMessages.lastElementChild;
                    this.addVersionNavigator(lastMessage, messageId);
                }

                // Clear pending
                this.pendingVersionMessageId = null;
                this.pendingVersions = null;
            }

            // Async refresh
            this.loadSessions().catch(err => console.error('Failed to refresh sessions:', err));
        } catch (error) {
            if (this.thinkMode) {
                this.hideThinking();
            }
            this.addMessage('抱歉，发生错误。请稍后重试。', 'assistant', 'error');
            console.error('Error:', error);
        }
    }

    showThinking(agent = 'Assistant') {
        const thinkingIndicator = document.getElementById('thinkingIndicator');
        const thinkingAgent = document.getElementById('thinkingAgent');
        if (thinkingIndicator && thinkingAgent) {
            thinkingAgent.textContent = agent;
            thinkingIndicator.style.display = 'flex';
            this.isLoading = true;
        }
    }

    hideThinking() {
        const thinkingIndicator = document.getElementById('thinkingIndicator');
        if (thinkingIndicator) {
            thinkingIndicator.style.display = 'none';
            this.isLoading = false;
            this.sendButton.disabled = !this.messageInput.value.trim();
        }
    }

    getAgentIcon(agentType) {
        switch (agentType) {
            case 'researcher':
                return '🔍';
            case 'coder':
                return '💻';
            case 'router':
                return '🔄';
            case 'visualizer':
                return '📊';
            case 'error':
                return '⚠️';
            default:
                return '🤖';
        }
    }

    addMessage(content, role, agentType = null, messageId = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;
        if (messageId) messageDiv.dataset.messageId = messageId;

        let headerHtml = '';
        if (role === 'assistant' && agentType) {
            headerHtml = `
                <div class="agent-badge">
                    <span>${this.getAgentIcon(agentType)}</span>
                    <span style="text-transform: capitalize">${agentType.replace('_', ' ')}</span>
                </div>
            `;
        }

        const isUser = role === 'user';

        messageDiv.innerHTML = `
            ${headerHtml}
            <div class="${isUser ? 'message-user-editable' : ''}">
                <div class="message-content markdown-body" data-original-content="${content}">
                    ${marked.parse(content)}
                </div>
                ${isUser ? `
                <div class="user-message-actions">
                    <div class="version-navigator-compact">
                        <button class="nav-btn prev" disabled>‹</button>
                        <span class="version-info">1/1</span>
                        <button class="nav-btn next" disabled>›</button>
                    </div>
                    <button class="user-action-btn edit-btn" title="Edit" onclick="app.editMessage(this)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="user-action-btn copy-btn" title="Copy" onclick="app.copyMessage(this)" data-content="${content}">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                        </svg>
                    </button>
                </div>
                ` : ''}
            </div>
            ${role === 'assistant' ? `
            <div class="message-actions">
                <button class="message-action-btn" onclick="app.copyMessage(this)" data-content="${content}">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                    </svg>
                    Copy
                </button>
                <button class="message-action-btn" onclick="app.regenerateMessage()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                    </svg>
                    Regenerate
                </button>
            </div>
            ` : ''}
        `;

        messageDiv.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });

        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    copyMessage(button) {
        const content = button.dataset.content;
        navigator.clipboard.writeText(content).then(() => {
            const originalHTML = button.innerHTML;
            button.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                已复制
            `;
            button.classList.add('active');
            setTimeout(() => {
                button.innerHTML = originalHTML;
                button.classList.remove('active');
            }, 2000);
        }).catch(err => console.error('Copy failed:', err));
    }

    likeMessage(button) {
        button.classList.toggle('active');
        // TODO: Send feedback to backend
    }

    dislikeMessage(button) {
        button.classList.toggle('active');
        // TODO: Send feedback to backend
    }

    regenerateMessage() {
        // TODO: Implement regenerate last message
        console.log('Regenerate message');
    }

    editMessage(button) {
        const messageDiv = button.closest('.message');
        const contentDiv = messageDiv.querySelector('.message-content');
        const originalContent = contentDiv.dataset.originalContent;

        // Create edit form
        const editForm = document.createElement('div');
        editForm.className = 'message-edit-form';
        editForm.innerHTML = `
            <textarea class="message-edit-input">${originalContent}</textarea>
            <div class="message-edit-actions">
                <button class="edit-action-btn edit-cancel-btn" onclick="app.cancelEdit(this)">取消</button>
                <button class="edit-action-btn edit-save-btn" onclick="app.saveEdit(this)">保存并重新生成</button>
            </div>
        `;

        // Replace content with edit form
        contentDiv.style.display = 'none';
        messageDiv.querySelector('.user-message-actions').style.display = 'none';
        messageDiv.appendChild(editForm);

        // Focus textarea
        const textarea = editForm.querySelector('textarea');
        textarea.focus();
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    }

    cancelEdit(button) {
        const messageDiv = button.closest('.message');
        const contentDiv = messageDiv.querySelector('.message-content');
        const editForm = messageDiv.querySelector('.message-edit-form');

        editForm.remove();
        contentDiv.style.display = 'block';
    }

    async saveEdit(button) {
        const messageDiv = button.closest('.message');
        const textarea = messageDiv.querySelector('.message-edit-input');
        const newContent = textarea.value.trim();

        if (!newContent) return;

        // Generate unique ID for this message pair
        const messageId = `msg_${Date.now()}`;

        // Remove all messages after this one and store as versions
        let nextMessage = messageDiv.nextElementSibling;
        const versions = [];

        while (nextMessage) {
            if (nextMessage.classList.contains('message-assistant')) {
                const content = nextMessage.querySelector('.message-content').textContent;
                const agentBadge = nextMessage.querySelector('.agent-badge');
                const agent = agentBadge ? agentBadge.textContent.split(' ')[1] : 'Assistant';

                versions.push({
                    content: content,
                    agent: agent,
                    timestamp: new Date().toISOString()
                });
            }

            const toRemove = nextMessage;
            nextMessage = nextMessage.nextElementSibling;
            toRemove.remove();
        }

        // Update message content DISPLAY
        const contentDiv = messageDiv.querySelector('.message-content');
        contentDiv.innerHTML = markdownRenderer.escapeHtml(newContent);
        contentDiv.dataset.originalContent = newContent; // Store unescaped for editing
        contentDiv.style.display = 'block';

        // Remove edit form
        messageDiv.querySelector('.message-edit-form').remove();

        // Store message ID for version tracking
        messageDiv.dataset.messageId = messageId;

        // Re-send message and get new response
        if (this.thinkMode) {
            this.showThinking('Assistant');
        }

        // Temporarily store a callback to handle the new response
        this.pendingVersionMessageId = messageId;
        this.pendingVersions = versions;

        // Send via API directly without using input field
        try {
            const selectedModel = this.modelSelect.value;
            const response = await apiClient.sendMessage(newContent, this.currentSessionId, selectedModel);

            if (this.thinkMode) {
                this.hideThinking();
            }

            this.addMessage(response.response, 'assistant', response.agent_type);

            // Handle version history
            if (this.pendingVersionMessageId) {
                const msgId = this.pendingVersionMessageId;
                const vers = this.pendingVersions || [];

                vers.push({
                    content: response.response,
                    agent: response.agent_type || 'Assistant',
                    timestamp: new Date().toISOString()
                });

                this.messageVersions.set(msgId, vers);

                if (vers.length > 1) {
                    const lastMessage = this.chatMessages.lastElementChild;
                    this.addVersionNavigator(lastMessage, msgId);
                }

                this.pendingVersionMessageId = null;
                this.pendingVersions = null;
            }

            this.loadSessions().catch(err => console.error('Failed to refresh sessions:', err));
        } catch (error) {
            if (this.thinkMode) {
                this.hideThinking();
            }
            this.addMessage('抱歉，发生错误。请稍后重试。', 'assistant', 'error');
            console.error('Error:', error);
        }
    }

    addVersionNavigator(messageDiv, messageId) {
        // Remove existing navigator if any
        const existing = messageDiv.querySelector('.version-navigator');
        if (existing) existing.remove();

        const versions = this.messageVersions.get(messageId);
        if (!versions || versions.length <= 1) return;

        // Create navigator
        const navigator = document.createElement('div');
        navigator.className = 'version-navigator';
        navigator.dataset.messageId = messageId;
        navigator.dataset.currentVersion = versions.length - 1; // Show latest by default

        navigator.innerHTML = `
            <button class="version-nav-btn" onclick="app.showPreviousVersion('${messageId}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M15 18l-6-6 6-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            <span class="version-counter">${versions.length}/${versions.length}</span>
            <button class="version-nav-btn" onclick="app.showNextVersion('${messageId}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M9 18l6-6-6-6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        `;

        // Insert before message actions
        const messageActions = messageDiv.querySelector('.message-actions');
        messageDiv.insertBefore(navigator, messageActions);
    }

    showPreviousVersion(messageId) {
        const versions = this.messageVersions.get(messageId);
        if (!versions) return;

        // Find the message with this navigator
        const navigator = this.chatMessages.querySelector(`.version-navigator[data-message-id="${messageId}"]`);
        if (navigator) {
            const messageDiv = navigator.closest('.message');
            this.switchVersion(messageId, messageDiv, versions, -1);
        }
    }

    showNextVersion(messageId) {
        const versions = this.messageVersions.get(messageId);
        if (!versions) return;

        const navigator = this.chatMessages.querySelector(`.version-navigator[data-message-id="${messageId}"]`);
        if (navigator) {
            const messageDiv = navigator.closest('.message');
            this.switchVersion(messageId, messageDiv, versions, 1);
        }
    }

    switchVersion(messageId, messageDiv, versions, direction) {
        const navigator = messageDiv.querySelector('.version-navigator');
        if (!navigator) return;

        let currentIdx = parseInt(navigator.dataset.currentVersion);
        currentIdx += direction;

        // Clamp to valid range (no wrap around for better UX)
        if (currentIdx < 0) currentIdx = 0;
        if (currentIdx >= versions.length) currentIdx = versions.length - 1;

        const version = versions[currentIdx];

        // Update content
        const contentDiv = messageDiv.querySelector('.message-content');
        contentDiv.innerHTML = markdownRenderer.render(version.content);

        // Update agent badge
        const agentBadge = messageDiv.querySelector('.agent-badge');
        if (agentBadge) {
            const agentConfig = {
                researcher: { icon: '🔍', name: 'Researcher' },
                coder: { icon: '💻', name: 'Coder' },
                general_assistant: { icon: '💬', name: 'Assistant' }
            };
            const config = agentConfig[version.agent] || agentConfig.general_assistant;
            agentBadge.innerHTML = `${config.icon} ${config.name}`;
        }

        // Update counter
        navigator.dataset.currentVersion = currentIdx;
        const counter = navigator.querySelector('.version-counter');
        counter.textContent = `${currentIdx + 1}/${versions.length}`;

        // Update button states
        const prevBtn = navigator.querySelectorAll('.version-nav-btn')[0];
        const nextBtn = navigator.querySelectorAll('.version-nav-btn')[1];

        prevBtn.disabled = currentIdx === 0;
        nextBtn.disabled = currentIdx === versions.length - 1;

        // Re-highlight code
        messageDiv.querySelectorAll('pre code').forEach(block => {
            hljs.highlightElement(block);
        });
    }

    getAgentBadge(agent) {
        const agentConfig = {
            researcher: { icon: '🔍', name: 'Researcher' },
            coder: { icon: '💻', name: 'Coder' },
            general_assistant: { icon: '💬', name: 'Assistant' }
        };

        const config = agentConfig[agent] || agentConfig.general_assistant;
        return `<div class="agent-badge">${config.icon} ${config.name}</div>`;
    }

    setLoading(loading) {
        this.isLoading = loading;
        this.loadingIndicator.style.display = loading ? 'flex' : 'none';
        this.sendButton.disabled = loading || !this.messageInput.value.trim();
    }

    copyToClipboard(button) {
        const content = button.dataset.content;
        navigator.clipboard.writeText(content).then(() => {
            button.textContent = '✓ 已复制';
            setTimeout(() => {
                button.textContent = '📋 复制';
            }, 2000);
        }).catch(err => {
            console.error('Copy failed:', err);
        });
    }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new AgenticChatApp();
});
