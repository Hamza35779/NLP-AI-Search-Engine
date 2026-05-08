/* Search History and Bookmarks Management */

class SearchHistory {
    constructor(maxItems = 50) {
        this.maxItems = maxItems;
        this.storageKey = 'nlp_search_history';
        this.history = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
    }

    add(query, resultCount) {
        if (!query) return;
        // Remove duplicate if exists
        this.history = this.history.filter(h => h.query !== query);
        // Add to beginning
        this.history.unshift({
            query: query,
            resultCount: resultCount,
            timestamp: Date.now()
        });
        // Trim to max
        this.history = this.history.slice(0, this.maxItems);
        this.save();
    }

    clear() {
        this.history = [];
        this.save();
    }

    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.history));
        this.updateCount();
    }

    updateCount() {
        const el = document.getElementById('history-count');
        if (el) el.textContent = this.history.length;
    }

    render(container) {
        if (!container) return;
        if (this.history.length === 0) {
            container.innerHTML = '<li class="empty-state">No search history yet</li>';
            return;
        }
        container.innerHTML = this.history.map(h => `
            <li class="history-item">
                <a href="/search?q=${encodeURIComponent(h.query)}">
                    <span class="query">${this.escapeHtml(h.query)}</span>
                    <span class="meta">${h.resultCount} results</span>
                </a>
            </li>
        `).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

class BookmarkManager {
    constructor() {
        this.storageKey = 'nlp_search_bookmarks';
        this.bookmarks = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
    }

    toggle(result) {
        const idx = this.bookmarks.findIndex(b => b.doc_id === result.doc_id);
        if (idx > -1) {
            this.bookmarks.splice(idx, 1);
        } else {
            this.bookmarks.push({
                doc_id: result.doc_id,
                title: result.title,
                snippet: result.snippet,
                score: result.score,
                source: result.source,
                url: result.url,
                domain: result.domain,
                savedAt: Date.now()
            });
        }
        this.save();
        return idx === -1; // returns true if added
    }

    isBookmarked(docId) {
        return this.bookmarks.some(b => b.doc_id === docId);
    }

    remove(docId) {
        this.bookmarks = this.bookmarks.filter(b => b.doc_id !== docId);
        this.save();
    }

    clear() {
        this.bookmarks = [];
        this.save();
    }

    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.bookmarks));
        this.updateCount();
    }

    updateCount() {
        const el = document.getElementById('bookmarks-count');
        if (el) el.textContent = this.bookmarks.length;
    }

    render(container) {
        if (!container) return;
        if (this.bookmarks.length === 0) {
            container.innerHTML = '<li class="empty-state">No bookmarks yet</li>';
            return;
        }
        container.innerHTML = this.bookmarks.map(b => `
            <li class="bookmark-item" data-doc-id="${b.doc_id}">
                <a href="${b.url || '#'}" ${b.url ? 'target="_blank"' : ''}>
                    <span class="title">${this.escapeHtml(b.title)}</span>
                    <span class="snippet">${this.stripHtml(b.snippet).substring(0, 100)}...</span>
                </a>
                <button class="remove-btn" onclick="bookmarks.remove(${b.doc_id}); bookmarks.render(document.getElementById('bookmarks-list')); event.stopPropagation();">×</button>
            </li>
        `).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    stripHtml(html) {
        const tmp = document.createElement('div');
        tmp.innerHTML = html;
        return tmp.textContent || tmp.innerText || '';
    }
}

// Theme Management
class ThemeManager {
    constructor() {
        this.themeKey = 'nlp_search_theme';
        this.current = localStorage.getItem(this.themeKey) || 'dark';
        this.applyTheme();
    }

    toggle() {
        this.current = this.current === 'dark' ? 'light' : 'dark';
        localStorage.setItem(this.themeKey, this.current);
        this.applyTheme();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.current);
        const lightIcon = document.getElementById('theme-icon-light');
        const darkIcon = document.getElementById('theme-icon-dark');
        if (lightIcon && darkIcon) {
            lightIcon.style.display = this.current === 'light' ? 'block' : 'none';
            darkIcon.style.display = this.current === 'dark' ? 'block' : 'none';
        }
    }
}

// Initialize
const history = new SearchHistory();
const bookmarks = new BookmarkManager();
const theme = new ThemeManager();

// Track search on results page
document.addEventListener('DOMContentLoaded', function() {
    const resultsSection = document.querySelector('.results-main');
    if (resultsSection) {
        const query = new URLSearchParams(window.location.search).get('q');
        const resultCount = document.querySelectorAll('.result').length;
        if (query) {
            history.add(query, resultCount);
        }
    }

    // Update counts on load
    history.updateCount();
    bookmarks.updateCount();

    // Panel toggles
    const historyToggle = document.getElementById('history-toggle');
    const historyPanel = document.getElementById('history-panel');
    const bookmarksToggle = document.getElementById('bookmarks-toggle');
    const bookmarksPanel = document.getElementById('bookmarks-panel');
    const themeToggle = document.getElementById('theme-toggle');

    if (historyToggle && historyPanel) {
        historyToggle.addEventListener('click', () => {
            history.render(document.getElementById('history-list'));
            historyPanel.style.display = historyPanel.style.display === 'none' ? 'block' : 'none';
            if (bookmarksPanel) bookmarksPanel.style.display = 'none';
        });
    }

    if (bookmarksToggle && bookmarksPanel) {
        bookmarksToggle.addEventListener('click', () => {
            bookmarks.render(document.getElementById('bookmarks-list'));
            bookmarksPanel.style.display = bookmarksPanel.style.display === 'none' ? 'block' : 'none';
            if (historyPanel) historyPanel.style.display = 'none';
        });
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => theme.toggle());
    }

    // Clear history button
    const clearHistoryBtn = document.getElementById('clear-history');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', () => {
            history.clear();
            history.render(document.getElementById('history-list'));
        });
    }

    // Clear bookmarks button
    const clearBookmarksBtn = document.getElementById('clear-bookmarks');
    if (clearBookmarksBtn) {
        clearBookmarksBtn.addEventListener('click', () => {
            bookmarks.clear();
            bookmarks.render(document.getElementById('bookmarks-list'));
        });
    }

    // Add bookmark buttons to results
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        const resultData = JSON.parse(btn.dataset.result || '{}');
        if (bookmarks.isBookmarked(resultData.doc_id)) {
            btn.classList.add('active');
        }
        btn.addEventListener('click', () => {
            const added = bookmarks.toggle(resultData);
            btn.classList.toggle('active');
            bookmarks.render(document.getElementById('bookmarks-list'));
        });
    });
});
