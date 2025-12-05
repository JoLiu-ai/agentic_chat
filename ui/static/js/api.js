/**
 * API Client Module - Enhanced
 * Handles all backend communication
 */

const API_BASE = '/api/v1';

class APIClient {
    constructor() {
        this.currentSessionId = null;
        this.currentModel = 'gpt-4o';
    }

    /**
     * Send a chat message
     */
    async sendMessage(message, sessionId, model = null) {
        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    session_id: sessionId,
                    user_id: 'default_user',
                    model: model || this.currentModel
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    // ========== Session APIs ==========

    async getSessions() {
        const response = await fetch(`${API_BASE}/sessions`);
        if (!response.ok) throw new Error('Failed to fetch sessions');
        return await response.json();
    }

    async getStarredSessions() {
        const response = await fetch(`${API_BASE}/sessions/starred`);
        if (!response.ok) throw new Error('Failed to fetch starred sessions');
        return await response.json();
    }

    async getSession(sessionId) {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
        if (!response.ok) throw new Error('Session not found');
        return await response.json();
    }

    async getSessionMessages(sessionId) {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
        if (!response.ok) throw new Error('Failed to fetch messages');
        return await response.json();
    }

    async createSession(title = null, projectId = null) {
        const response = await fetch(`${API_BASE}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 'default_user',
                title: title || '新对话',
                project_id: projectId
            })
        });
        if (!response.ok) throw new Error('Failed to create session');
        return await response.json();
    }

    async updateSession(sessionId, updates) {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        if (!response.ok) throw new Error('Failed to update session');
        return await response.json();
    }

    async deleteSession(sessionId) {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete session');
        return await response.json();
    }

    async toggleStar(sessionId, targetState) {
        return this.updateSession(sessionId, { is_starred: targetState });
    }

    // ========== Project APIs ==========

    async getProjects() {
        const response = await fetch(`${API_BASE}/projects`);
        if (!response.ok) throw new Error('Failed to fetch projects');
        return await response.json();
    }

    async createProject(name, description = null, color = 'blue', icon = '📁') {
        const response = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                description,
                color,
                icon,
                user_id: 'default_user'
            })
        });
        if (!response.ok) throw new Error('Failed to create project');
        return await response.json();
    }

    async deleteProject(projectId) {
        const response = await fetch(`${API_BASE}/projects/${projectId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete project');
        return await response.json();
    }

    // ========== Message APIs ==========

    async deleteMessage(messageId) {
        const response = await fetch(`${API_BASE}/messages/${messageId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete message');
        return await response.json();
    }

    async deleteMessagesAfter(messageId) {
        const response = await fetch(`${API_BASE}/messages/${messageId}/after`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete messages');
        return await response.json();
    }

    async updateMessage(messageId, content) {
        const response = await fetch(`${API_BASE}/messages/${messageId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });
        if (!response.ok) throw new Error('Failed to update message');
        return await response.json();
    }

    // ========== Utility ==========

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    setModel(model) {
        this.currentModel = model;
    }

    getModel() {
        return this.currentModel;
    }
}

// Export singleton instance
const apiClient = new APIClient();
