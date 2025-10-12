/**
 * مدير البحث العام
 * يوفر وظائف البحث المتقدم في النظام
 */

class SearchManager {
    constructor() {
        this.apiClient = apiClient;
        this.searchInput = null;
        this.searchResults = null;
        this.searchOverlay = null;
        this.currentQuery = '';
        this.searchTimeout = null;
        this.isSearching = false;
        this.recentSearches = this.loadRecentSearches();
        this.init();
    }

    /**
     * تهيئة مدير البحث
     */
    init() {
        this.setupSearchElements();
        this.setupEventListeners();
        this.createSearchOverlay();
    }

    /**
     * إعداد عناصر البحث في DOM
     */
    setupSearchElements() {
        this.searchInput = document.getElementById('globalSearch');
        
        if (!this.searchInput) {
            console.warn('Search input not found in DOM');
            return;
        }
    }

    /**
     * إعداد مستمعي الأحداث
     */
    setupEventListeners() {
        if (!this.searchInput) return;

        // البحث أثناء الكتابة
        this.searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        // التركيز على حقل البحث
        this.searchInput.addEventListener('focus', () => {
            this.showSearchOverlay();
        });

        // الضغط على مفاتيح خاصة
        this.searchInput.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });

        // اختصار لوحة المفاتيح للبحث (Ctrl+K أو Cmd+K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.focusSearch();
            }
            
            // إغلاق البحث بـ Escape
            if (e.key === 'Escape') {
                this.hideSearchOverlay();
            }
        });

        // إغلاق البحث عند النقر خارجه
        document.addEventListener('click', (e) => {
            if (!this.searchInput.closest('.search-box').contains(e.target) && 
                !this.searchOverlay?.contains(e.target)) {
                this.hideSearchOverlay();
            }
        });
    }

    /**
     * إنشاء overlay البحث
     */
    createSearchOverlay() {
        this.searchOverlay = document.createElement('div');
        this.searchOverlay.className = 'search-overlay';
        this.searchOverlay.innerHTML = `
            <div class="search-container">
                <div class="search-header">
                    <h3>البحث في النظام</h3>
                    <button class="close-search">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="search-content">
                    <div class="search-suggestions">
                        <div class="suggestions-section">
                            <h4>البحث السريع</h4>
                            <div class="quick-search-items">
                                <button class="quick-search-btn" data-query="المشاريع النشطة">
                                    <i class="fas fa-project-diagram"></i>
                                    المشاريع النشطة
                                </button>
                                <button class="quick-search-btn" data-query="المهام المعلقة">
                                    <i class="fas fa-tasks"></i>
                                    المهام المعلقة
                                </button>
                                <button class="quick-search-btn" data-query="الإشعارات الجديدة">
                                    <i class="fas fa-bell"></i>
                                    الإشعارات الجديدة
                                </button>
                                <button class="quick-search-btn" data-query="التقارير">
                                    <i class="fas fa-chart-bar"></i>
                                    التقارير
                                </button>
                            </div>
                        </div>
                        <div class="recent-searches-section">
                            <h4>عمليات البحث الأخيرة</h4>
                            <div class="recent-searches-list">
                                <!-- سيتم ملؤها بـ JavaScript -->
                            </div>
                        </div>
                    </div>
                    <div class="search-results-container">
                        <div class="search-loading">
                            <i class="fas fa-spinner fa-spin"></i>
                            <span>جاري البحث...</span>
                        </div>
                        <div class="search-results">
                            <!-- نتائج البحث -->
                        </div>
                        <div class="no-results">
                            <i class="fas fa-search"></i>
                            <h4>لا توجد نتائج</h4>
                            <p>جرب استخدام كلمات مختلفة أو تحقق من الإملاء</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(this.searchOverlay);
        this.setupOverlayEventListeners();
    }

    /**
     * إعداد مستمعي أحداث overlay البحث
     */
    setupOverlayEventListeners() {
        // إغلاق البحث
        const closeBtn = this.searchOverlay.querySelector('.close-search');
        closeBtn.addEventListener('click', () => {
            this.hideSearchOverlay();
        });

        // البحث السريع
        const quickSearchBtns = this.searchOverlay.querySelectorAll('.quick-search-btn');
        quickSearchBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                this.performQuickSearch(query);
            });
        });

        // النقر على نتيجة بحث
        this.searchOverlay.addEventListener('click', (e) => {
            const resultItem = e.target.closest('.search-result-item');
            if (resultItem) {
                this.handleResultClick(resultItem);
            }
        });
    }

    /**
     * معالجة إدخال البحث
     */
    handleSearchInput(query) {
        this.currentQuery = query.trim();
        
        // مسح timeout السابق
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }

        if (this.currentQuery.length === 0) {
            this.showSearchSuggestions();
            return;
        }

        if (this.currentQuery.length < 2) {
            return;
        }

        // تأخير البحث لتجنب الطلبات المتكررة
        this.searchTimeout = setTimeout(() => {
            this.performSearch(this.currentQuery);
        }, 300);
    }

    /**
     * معالجة الضغط على المفاتيح
     */
    handleKeyDown(e) {
        const resultsContainer = this.searchOverlay.querySelector('.search-results');
        const results = resultsContainer.querySelectorAll('.search-result-item');
        
        if (results.length === 0) return;

        const currentActive = resultsContainer.querySelector('.search-result-item.active');
        let activeIndex = -1;
        
        if (currentActive) {
            activeIndex = Array.from(results).indexOf(currentActive);
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                activeIndex = Math.min(activeIndex + 1, results.length - 1);
                this.setActiveResult(results, activeIndex);
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                this.setActiveResult(results, activeIndex);
                break;
                
            case 'Enter':
                e.preventDefault();
                if (currentActive) {
                    this.handleResultClick(currentActive);
                } else if (results.length > 0) {
                    this.handleResultClick(results[0]);
                }
                break;
        }
    }

    /**
     * تعيين النتيجة النشطة
     */
    setActiveResult(results, activeIndex) {
        results.forEach((result, index) => {
            if (index === activeIndex) {
                result.classList.add('active');
                result.scrollIntoView({ block: 'nearest' });
            } else {
                result.classList.remove('active');
            }
        });
    }

    /**
     * التركيز على حقل البحث
     */
    focusSearch() {
        if (this.searchInput) {
            this.searchInput.focus();
            this.showSearchOverlay();
        }
    }

    /**
     * إظهار overlay البحث
     */
    showSearchOverlay() {
        if (this.searchOverlay) {
            this.searchOverlay.classList.add('show');
            document.body.classList.add('search-overlay-open');
            
            if (this.currentQuery.length === 0) {
                this.showSearchSuggestions();
            }
        }
    }

    /**
     * إخفاء overlay البحث
     */
    hideSearchOverlay() {
        if (this.searchOverlay) {
            this.searchOverlay.classList.remove('show');
            document.body.classList.remove('search-overlay-open');
            this.searchInput.blur();
        }
    }

    /**
     * إظهار اقتراحات البحث
     */
    showSearchSuggestions() {
        const suggestionsSection = this.searchOverlay.querySelector('.search-suggestions');
        const resultsContainer = this.searchOverlay.querySelector('.search-results-container');
        
        suggestionsSection.style.display = 'block';
        resultsContainer.style.display = 'none';
        
        this.renderRecentSearches();
    }

    /**
     * عرض عمليات البحث الأخيرة
     */
    renderRecentSearches() {
        const recentSearchesList = this.searchOverlay.querySelector('.recent-searches-list');
        
        if (this.recentSearches.length === 0) {
            recentSearchesList.innerHTML = '<p class="no-recent">لا توجد عمليات بحث سابقة</p>';
            return;
        }

        const recentHTML = this.recentSearches.map(search => `
            <button class="recent-search-item" data-query="${search}">
                <i class="fas fa-history"></i>
                <span>${search}</span>
                <button class="remove-recent" data-query="${search}">
                    <i class="fas fa-times"></i>
                </button>
            </button>
        `).join('');

        recentSearchesList.innerHTML = recentHTML;

        // إضافة مستمعي الأحداث
        recentSearchesList.addEventListener('click', (e) => {
            if (e.target.closest('.remove-recent')) {
                const query = e.target.closest('.remove-recent').dataset.query;
                this.removeRecentSearch(query);
            } else if (e.target.closest('.recent-search-item')) {
                const query = e.target.closest('.recent-search-item').dataset.query;
                this.searchInput.value = query;
                this.performSearch(query);
            }
        });
    }

    /**
     * تنفيذ البحث
     */
    async performSearch(query) {
        if (!this.apiClient.isAuthenticated() || this.isSearching) {
            return;
        }

        this.isSearching = true;
        this.showSearchLoading();
        this.addToRecentSearches(query);

        try {
            const response = await this.apiClient.search(query);
            
            if (response.success) {
                this.displaySearchResults(response.results, query);
            } else {
                this.showNoResults();
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showSearchError();
        } finally {
            this.isSearching = false;
            this.hideSearchLoading();
        }
    }

    /**
     * تنفيذ البحث السريع
     */
    performQuickSearch(query) {
        this.searchInput.value = query;
        this.currentQuery = query;
        this.performSearch(query);
    }

    /**
     * إظهار مؤشر التحميل
     */
    showSearchLoading() {
        const suggestionsSection = this.searchOverlay.querySelector('.search-suggestions');
        const resultsContainer = this.searchOverlay.querySelector('.search-results-container');
        const loadingDiv = this.searchOverlay.querySelector('.search-loading');
        
        suggestionsSection.style.display = 'none';
        resultsContainer.style.display = 'block';
        loadingDiv.style.display = 'flex';
    }

    /**
     * إخفاء مؤشر التحميل
     */
    hideSearchLoading() {
        const loadingDiv = this.searchOverlay.querySelector('.search-loading');
        loadingDiv.style.display = 'none';
    }

    /**
     * عرض نتائج البحث
     */
    displaySearchResults(results, query) {
        const resultsDiv = this.searchOverlay.querySelector('.search-results');
        const noResultsDiv = this.searchOverlay.querySelector('.no-results');
        
        if (results.length === 0) {
            this.showNoResults();
            return;
        }

        noResultsDiv.style.display = 'none';
        resultsDiv.style.display = 'block';

        // تجميع النتائج حسب النوع
        const groupedResults = this.groupResultsByType(results);
        
        let resultsHTML = `<div class="search-results-header">
            <h4>نتائج البحث عن: "${query}"</h4>
            <span class="results-count">${results.length} نتيجة</span>
        </div>`;

        Object.keys(groupedResults).forEach(type => {
            const typeResults = groupedResults[type];
            const typeName = this.getTypeDisplayName(type);
            
            resultsHTML += `
                <div class="results-group">
                    <h5 class="results-group-title">
                        ${this.getTypeIcon(type)}
                        ${typeName} (${typeResults.length})
                    </h5>
                    <div class="results-group-items">
                        ${typeResults.map(result => this.createResultHTML(result)).join('')}
                    </div>
                </div>
            `;
        });

        resultsDiv.innerHTML = resultsHTML;
    }

    /**
     * تجميع النتائج حسب النوع
     */
    groupResultsByType(results) {
        const grouped = {};
        
        results.forEach(result => {
            if (!grouped[result.type]) {
                grouped[result.type] = [];
            }
            grouped[result.type].push(result);
        });
        
        return grouped;
    }

    /**
     * الحصول على اسم النوع للعرض
     */
    getTypeDisplayName(type) {
        const typeNames = {
            'project': 'المشاريع',
            'task': 'المهام',
            'user': 'المستخدمون',
            'blog': 'المقالات',
            'page': 'الصفحات'
        };
        
        return typeNames[type] || type;
    }

    /**
     * الحصول على أيقونة النوع
     */
    getTypeIcon(type) {
        const typeIcons = {
            'project': '<i class="fas fa-project-diagram"></i>',
            'task': '<i class="fas fa-tasks"></i>',
            'user': '<i class="fas fa-user"></i>',
            'blog': '<i class="fas fa-blog"></i>',
            'page': '<i class="fas fa-file-alt"></i>'
        };
        
        return typeIcons[type] || '<i class="fas fa-search"></i>';
    }

    /**
     * إنشاء HTML لنتيجة بحث
     */
    createResultHTML(result) {
        return `
            <div class="search-result-item" data-type="${result.type}" data-id="${result.id}" data-url="${result.url}">
                <div class="result-icon">
                    ${this.getTypeIcon(result.type)}
                </div>
                <div class="result-content">
                    <div class="result-title">${this.highlightQuery(result.title, this.currentQuery)}</div>
                    <div class="result-description">${this.highlightQuery(result.description, this.currentQuery)}</div>
                    <div class="result-meta">
                        <span class="result-type">${this.getTypeDisplayName(result.type)}</span>
                        <span class="result-relevance">الصلة: ${Math.round(result.relevance_score * 100)}%</span>
                    </div>
                </div>
                <div class="result-actions">
                    <button class="goto-result" title="انتقال">
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * تمييز كلمة البحث في النص
     */
    highlightQuery(text, query) {
        if (!query || !text) return text;
        
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * إظهار رسالة عدم وجود نتائج
     */
    showNoResults() {
        const resultsDiv = this.searchOverlay.querySelector('.search-results');
        const noResultsDiv = this.searchOverlay.querySelector('.no-results');
        
        resultsDiv.style.display = 'none';
        noResultsDiv.style.display = 'block';
    }

    /**
     * إظهار خطأ البحث
     */
    showSearchError() {
        const resultsDiv = this.searchOverlay.querySelector('.search-results');
        resultsDiv.innerHTML = `
            <div class="search-error">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>خطأ في البحث</h4>
                <p>حدث خطأ أثناء البحث. يرجى المحاولة مرة أخرى.</p>
            </div>
        `;
        resultsDiv.style.display = 'block';
    }

    /**
     * معالجة النقر على نتيجة البحث
     */
    handleResultClick(resultItem) {
        const url = resultItem.dataset.url;
        const type = resultItem.dataset.type;
        const id = resultItem.dataset.id;
        
        // إغلاق overlay البحث
        this.hideSearchOverlay();
        
        // التنقل إلى الصفحة
        if (url) {
            window.location.href = url;
        } else {
            // التنقل الافتراضي حسب النوع
            this.navigateToResult(type, id);
        }
    }

    /**
     * التنقل إلى النتيجة
     */
    navigateToResult(type, id) {
        const routes = {
            'project': `/admin-panel/pages/projects/project-detail.html?id=${id}`,
            'task': `/admin-panel/pages/tasks/task-detail.html?id=${id}`,
            'user': `/admin-panel/pages/users/user-detail.html?id=${id}`,
            'blog': `/admin-panel/pages/blog/post-detail.html?id=${id}`,
            'page': `/admin-panel/pages/content/page-detail.html?id=${id}`
        };
        
        const route = routes[type];
        if (route) {
            window.location.href = route;
        }
    }

    /**
     * إضافة إلى عمليات البحث الأخيرة
     */
    addToRecentSearches(query) {
        if (!query || query.length < 2) return;
        
        // إزالة البحث إذا كان موجوداً مسبقاً
        this.recentSearches = this.recentSearches.filter(search => search !== query);
        
        // إضافة في المقدمة
        this.recentSearches.unshift(query);
        
        // الاحتفاظ بآخر 10 عمليات بحث فقط
        this.recentSearches = this.recentSearches.slice(0, 10);
        
        // حفظ في localStorage
        this.saveRecentSearches();
    }

    /**
     * إزالة من عمليات البحث الأخيرة
     */
    removeRecentSearch(query) {
        this.recentSearches = this.recentSearches.filter(search => search !== query);
        this.saveRecentSearches();
        this.renderRecentSearches();
    }

    /**
     * تحميل عمليات البحث الأخيرة
     */
    loadRecentSearches() {
        try {
            const saved = localStorage.getItem('recent_searches');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            return [];
        }
    }

    /**
     * حفظ عمليات البحث الأخيرة
     */
    saveRecentSearches() {
        try {
            localStorage.setItem('recent_searches', JSON.stringify(this.recentSearches));
        } catch (error) {
            console.error('Error saving recent searches:', error);
        }
    }

    /**
     * مسح عمليات البحث الأخيرة
     */
    clearRecentSearches() {
        this.recentSearches = [];
        this.saveRecentSearches();
        this.renderRecentSearches();
    }

    /**
     * تنظيف الموارد
     */
    destroy() {
        if (this.searchTimeout) {
            clearTimeout(this.searchTimeout);
        }
        
        if (this.searchOverlay) {
            this.searchOverlay.remove();
        }
    }
}

// تهيئة مدير البحث عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    if (typeof apiClient !== 'undefined') {
        window.searchManager = new SearchManager();
    }
});

// تصدير للاستخدام في ملفات أخرى
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SearchManager;
}

