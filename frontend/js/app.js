/**
 * Digital Risk Shield - Main Application Logic
 * Full SPA controller, API integration, and reactive rendering
 */

// Global API Base URL Resolution & Interceptor:
// Transparently routes /api/* requests to a custom remote or deployed backend link if configured.
(function() {
  const originalFetch = window.fetch;
  window.fetch = function(input, init) {
    if (typeof input === 'string' && input.startsWith('/api/')) {
      const base = window.API_BASE_URL || localStorage.getItem('drs_api_base_url') || '';
      if (base) {
        input = base.replace(/\/+$/, '') + input;
      }
    }
    return originalFetch.call(this, input, init);
  };
})();

const App = {
  currentView: 'landing', // 'landing' or dashboard views: 'overview', 'brands', 'social', 'apps', 'analyzer', 'threats', 'reports', 'architecture', 'settings', 'help'
  selectedBrand: 'All Brands',
  brandsList: [],
  socialThreats: [],
  appThreats: [],
  unifiedThreats: [],
  selectedThreat: null,
  activeScanInterval: null,

  async init() {
    console.log("Initializing Digital Risk Shield...");
    this.bindEvents();
    this.initBackendSettings();
    await this.loadInitialData();
    this.checkSession();
    this.navigate(this.currentView);
    if (window.lucide) lucide.createIcons();
  },

  initBackendSettings() {
    const saved = localStorage.getItem('drs_api_base_url');
    if (saved) {
      window.API_BASE_URL = saved;
    }
    const input = document.getElementById('custom-backend-url-input');
    if (input) {
      input.value = saved || '';
    }
    this.updateBackendStatusBadge();
  },

  getBackendUrl() {
    return window.API_BASE_URL || localStorage.getItem('drs_api_base_url') || (window.location.origin !== 'null' && window.location.origin !== 'file://' ? window.location.origin : 'http://localhost:8000');
  },

  async saveBackendUrlFromInput() {
    const input = document.getElementById('custom-backend-url-input');
    if (!input) return;
    const val = input.value.trim();
    if (!val) {
      localStorage.removeItem('drs_api_base_url');
      delete window.API_BASE_URL;
      UI.showToast('Backend link reset to default origin.', 'info');
    } else {
      const clean = val.replace(/\/+$/, '');
      localStorage.setItem('drs_api_base_url', clean);
      window.API_BASE_URL = clean;
      UI.showToast(`Backend link updated to ${clean}`, 'success');
    }
    await this.loadInitialData();
    this.updateBackendStatusBadge();
  },

  async testBackendConnectionFromInput() {
    const input = document.getElementById('custom-backend-url-input');
    const targetUrl = (input && input.value.trim()) ? input.value.trim().replace(/\/+$/, '') : this.getBackendUrl();
    try {
      UI.showToast('Pinging backend /api/health...', 'info');
      const res = await fetch(`${targetUrl}/api/health`, { method: 'GET' });
      if (res.ok) {
        const data = await res.json();
        UI.showToast(`Connected successfully! Server: ${data.service || 'Digital Risk Shield'} (${data.version || '1.0.0'})`, 'success');
        this.updateBackendStatusBadge();
      } else {
        UI.showToast(`Server responded with HTTP status ${res.status}`, 'warning');
      }
    } catch (e) {
      UI.showToast(`Connection failed: Could not reach ${targetUrl}. Ensure CORS allows access and the server is running.`, 'error');
    }
  },

  async updateBackendStatusBadge() {
    const badge = document.getElementById('backend-status-badge');
    const textEl = document.getElementById('backend-status-text');
    if (!badge) return;
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        badge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30';
        if (textEl) textEl.textContent = 'Backend Online';
      } else {
        badge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30';
        if (textEl) textEl.textContent = 'Backend Degraded';
      }
    } catch (e) {
      badge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30';
      if (textEl) textEl.textContent = 'Backend Offline';
    }
  },

  checkSession() {
    const userStr = localStorage.getItem('drs_user');
    if (userStr) {
      try {
        AppData.currentUser = JSON.parse(userStr);
        this.updateUserBadge();
      } catch (e) {}
    }
  },

  updateUserBadge() {
    const el = document.getElementById('user-name-display');
    const roleEl = document.getElementById('user-role-display');
    if (el) el.textContent = AppData.currentUser.username;
    if (roleEl) roleEl.textContent = AppData.currentUser.role;
  },

  async loadInitialData() {
    try {
      const [brandsRes, statsRes] = await Promise.all([
        fetch('/api/brands').catch(() => null),
        fetch('/api/stats').catch(() => null)
      ]);

      if (brandsRes && brandsRes.ok) {
        this.brandsList = await brandsRes.json();
        this.populateBrandSelectors();
      }
      if (statsRes && statsRes.ok) {
        AppData.stats = await statsRes.json();
      }
    } catch (err) {
      console.warn("Using offline / fallback datasets:", err);
    }
  },

  populateBrandSelectors() {
    const selects = document.querySelectorAll('.brand-selector');
    selects.forEach(sel => {
      const current = sel.value;
      sel.innerHTML = `<option value="All Brands">All Monitored Brands</option>`;
      this.brandsList.forEach(b => {
        sel.innerHTML += `<option value="${b.name}">${b.name}</option>`;
      });
      if (current) sel.value = current;
    });
  },

  bindEvents() {
    // Brand selector change
    const brandSel = document.getElementById('global-brand-selector');
    if (brandSel) {
      brandSel.addEventListener('change', (e) => {
        this.selectedBrand = e.target.value;
        UI.showToast(`Active brand context set to: ${this.selectedBrand}`);
        this.refreshCurrentView();
      });
    }

    // Sidebar navigation clicks
    document.querySelectorAll('[data-nav]').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = item.getAttribute('data-nav');
        this.navigate(view);
      });
    });

    // Mobile sidebar toggle
    const toggleBtn = document.getElementById('sidebar-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('-translate-x-full');
      });
    }
  },

  navigate(viewName) {
    this.currentView = viewName;
    
    // Toggle between Landing Page and App Dashboard shell
    const landingSection = document.getElementById('landing-view');
    const dashboardShell = document.getElementById('dashboard-shell');
    
    if (viewName === 'landing') {
      if (landingSection) landingSection.classList.remove('hidden');
      if (dashboardShell) dashboardShell.classList.add('hidden');
      window.scrollTo(0, 0);
      return;
    } else {
      if (landingSection) landingSection.classList.add('hidden');
      if (dashboardShell) dashboardShell.classList.remove('hidden');
    }

    // Update active state in sidebar
    document.querySelectorAll('.nav-link').forEach(link => {
      const target = link.getAttribute('data-nav');
      if (target === viewName) {
        link.classList.add('bg-blue-600/20', 'text-cyan-400', 'border-r-2', 'border-cyan-400');
        link.classList.remove('text-slate-400');
      } else {
        link.classList.remove('bg-blue-600/20', 'text-cyan-400', 'border-r-2', 'border-cyan-400');
        link.classList.add('text-slate-400');
      }
    });

    // Hide all view containers, show selected
    document.querySelectorAll('.view-container').forEach(c => c.classList.add('hidden'));
    const activeContainer = document.getElementById(`view-${viewName}`);
    if (activeContainer) {
      activeContainer.classList.remove('hidden');
    }

    // Render corresponding view data
    this.refreshCurrentView();
    window.scrollTo(0, 0);
    if (window.lucide) lucide.createIcons();
  },

  refreshCurrentView() {
    switch (this.currentView) {
      case 'overview':
        this.renderOverview();
        break;
      case 'brands':
        this.renderBrands();
        break;
      case 'social':
        this.renderSocialMonitoring();
        break;
      case 'apps':
        this.renderAppMonitoring();
        break;
      case 'analyzer':
        this.initAnalyzerView();
        break;
      case 'threats':
        this.renderThreatInvestigation();
        break;
      case 'reports':
        this.renderReports();
        break;
      case 'architecture':
        // static interactive view
        break;
    }
    if (window.lucide) lucide.createIcons();
  },

  // ==========================================
  // 1. OVERVIEW / DASHBOARD
  // ==========================================
  async renderOverview() {
    try {
      const statsRes = await fetch('/api/stats');
      if (statsRes.ok) {
        AppData.stats = await statsRes.json();
      }
    } catch (e) {}

    const counters = AppData.stats.counters;
    document.getElementById('stat-total-brands').textContent = counters.total_brands || 3;
    document.getElementById('stat-social-analyzed').textContent = counters.social_analyzed || 55;
    document.getElementById('stat-apps-analyzed').textContent = counters.apps_analyzed || 36;
    document.getElementById('stat-potential-threats').textContent = counters.potential_threats || 9;
    document.getElementById('stat-critical-threats').textContent = counters.critical_threats || 4;
    document.getElementById('stat-resolved').textContent = counters.resolved_incidents || 2;

    // Render Recent Threats Table
    try {
      const threatsRes = await fetch('/api/threats');
      if (threatsRes.ok) {
        this.unifiedThreats = await threatsRes.json();
      }
    } catch (e) {}

    const tbody = document.getElementById('recent-threats-tbody');
    if (!tbody) return;

    let items = this.unifiedThreats;
    if (this.selectedBrand !== 'All Brands') {
      items = items.filter(t => t.brand_name === this.selectedBrand);
    }
    items = items.slice(0, 7); // Show top 7 recent

    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-500">No active threats detected for this brand context.</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(t => `
      <tr class="border-b border-slate-800/80 hover:bg-slate-800/40 transition">
        <td class="py-3 px-4">
          <div class="flex items-center gap-3">
            <img src="${t.icon || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=128&auto=format&fit=crop&q=80'}" class="w-8 h-8 rounded-lg object-cover border border-slate-700">
            <div>
              <div class="font-medium text-slate-200 text-sm">${t.account_name || t.app_name}</div>
              <div class="text-xs text-slate-400 font-mono">${t.username ? '@' + t.username : t.publisher}</div>
            </div>
          </div>
        </td>
        <td class="py-3 px-4">
          <div class="flex items-center gap-1.5 text-xs text-slate-300">
            ${UI.renderPlatformIcon(t.platform || t.store_name)}
            <span>${t.platform || t.store_name}</span>
          </div>
        </td>
        <td class="py-3 px-4 text-xs text-slate-400 font-medium">${t.brand_name}</td>
        <td class="py-3 px-4">${UI.renderRiskScore(t.risk_score)}</td>
        <td class="py-3 px-4">${UI.renderSeverityBadge(t.severity)}</td>
        <td class="py-3 px-4">${UI.renderStatusBadge(t.status)}</td>
        <td class="py-3 px-4 text-right">
          <button onclick="App.openThreatDetail('${t.type}', ${t.id})" class="px-2.5 py-1 text-xs font-medium rounded bg-blue-600/20 text-cyan-400 border border-blue-500/30 hover:bg-blue-600/30 transition">
            Investigate
          </button>
        </td>
      </tr>
    `).join('');

    // Re-render charts
    Charts.initAll(AppData.stats.charts);
    if (window.lucide) lucide.createIcons();
  },

  // ==========================================
  // 2. BRAND PROFILE MANAGEMENT
  // ==========================================
  async renderBrands() {
    try {
      const res = await fetch('/api/brands');
      if (res.ok) this.brandsList = await res.json();
    } catch (e) {}

    const container = document.getElementById('brands-grid');
    if (!container) return;

    if (this.brandsList.length === 0) {
      container.innerHTML = `<div class="col-span-3 text-center py-12 text-slate-500">No brand profiles registered yet. Click "Register New Brand" above.</div>`;
      return;
    }

    container.innerHTML = this.brandsList.map(b => `
      <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
        <div>
          <div class="flex items-start justify-between gap-4 mb-4">
            <div class="flex items-center gap-3">
              <img src="${b.logo_url || 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80'}" class="w-12 h-12 rounded-xl object-cover border border-slate-700/80 shadow-md">
              <div>
                <h3 class="font-semibold text-slate-100 text-base flex items-center gap-1.5">
                  ${b.name}
                  <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Protected</span>
                </h3>
                <span class="text-xs text-slate-400">${b.industry || 'Technology'}</span>
              </div>
            </div>
            <button onclick="App.deleteBrand(${b.id})" class="text-slate-500 hover:text-red-400 transition text-sm p-1" title="Delete Brand Profile">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>

          <p class="text-xs text-slate-300 line-clamp-2 mb-4 leading-relaxed">${b.description || 'Enterprise protected brand profile.'}</p>

          <div class="space-y-2 mb-4">
            <div class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
              <i data-lucide="shield-check" class="w-3.5 h-3.5 text-cyan-400"></i> Whitelisted Assets (Exclusion Rules)
            </div>
            <div class="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800/80 text-xs space-y-1.5 font-mono">
              <div class="flex items-center gap-2 truncate text-slate-300">
                <span class="text-slate-500">Web:</span>
                <a href="${b.official_website}" target="_blank" class="text-cyan-400 hover:underline truncate">${b.official_website || 'None'}</a>
              </div>
              <div class="flex items-center gap-2 truncate text-slate-300">
                <span class="text-slate-500">Socials:</span>
                <span class="text-slate-300 truncate">${(b.official_social_urls || []).length} registered channels</span>
              </div>
              <div class="flex items-center gap-2 truncate text-slate-300">
                <span class="text-slate-500">Publishers:</span>
                <span class="text-slate-300 truncate">${(b.verified_publishers || []).join(', ') || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>Active Risk Monitoring: <b class="text-emerald-400">24/7</b></span>
          <button onclick="App.openBrandDetailsModal(${b.id})" class="text-cyan-400 hover:underline flex items-center gap-1 font-medium">
            View Assets <i data-lucide="chevron-right" class="w-3 h-3"></i>
          </button>
        </div>
      </div>
    `).join('');

    if (window.lucide) lucide.createIcons();
  },

  async handleCreateBrand(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {
      name: form.name.value.trim(),
      industry: form.industry.value.trim(),
      official_website: form.official_website.value.trim(),
      description: form.description.value.trim(),
      logo_url: form.logo_url.value.trim() || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80",
      official_social_urls: form.official_social_urls.value.split('\n').map(s => s.trim()).filter(Boolean),
      official_app_names: form.official_app_names.value.split(',').map(s => s.trim()).filter(Boolean),
      verified_publishers: form.verified_publishers.value.split(',').map(s => s.trim()).filter(Boolean),
      brand_keywords: form.brand_keywords.value.split(',').map(s => s.trim()).filter(Boolean)
    };

    try {
      const res = await fetch('/api/brands', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        UI.showToast(`Brand "${payload.name}" successfully registered!`, 'success');
        UI.closeModal('modal-add-brand');
        form.reset();
        await this.loadInitialData();
        this.renderBrands();
      } else {
        const err = await res.json();
        UI.showToast(`Error: ${err.detail || 'Could not register brand'}`, 'error');
      }
    } catch (err) {
      UI.showToast('Network error while saving brand.', 'error');
    }
  },

  async deleteBrand(brandId) {
    if (!confirm('Are you sure you want to delete this brand profile and its asset whitelist?')) return;
    try {
      const res = await fetch(`/api/brands/${brandId}`, { method: 'DELETE' });
      if (res.ok) {
        UI.showToast('Brand deleted.', 'info');
        await this.loadInitialData();
        this.renderBrands();
      }
    } catch (e) {
      UI.showToast('Failed to delete brand.', 'error');
    }
  },

  openBrandDetailsModal(brandId) {
    const brand = this.brandsList.find(b => b.id === brandId);
    if (!brand) return;
    
    document.getElementById('modal-brand-name').textContent = brand.name;
    document.getElementById('modal-brand-industry').textContent = brand.industry || 'Technology';
    document.getElementById('modal-brand-web').textContent = brand.official_website || 'None';
    document.getElementById('modal-brand-web').href = brand.official_website || '#';
    document.getElementById('modal-brand-desc').textContent = brand.description || 'No description provided.';
    
    const socialsList = document.getElementById('modal-brand-socials');
    socialsList.innerHTML = (brand.official_social_urls || []).map(u => `
      <li class="flex items-center gap-2 text-slate-300 font-mono text-xs">
        <i data-lucide="check-circle" class="w-3.5 h-3.5 text-emerald-400"></i>
        <a href="${u}" target="_blank" class="hover:underline text-cyan-400 truncate">${u}</a>
      </li>
    `).join('') || '<li class="text-slate-500">No social assets listed.</li>';

    const appsList = document.getElementById('modal-brand-apps');
    appsList.innerHTML = (brand.official_app_names || []).map(a => `
      <li class="flex items-center gap-2 text-slate-300 font-mono text-xs">
        <i data-lucide="check-circle" class="w-3.5 h-3.5 text-emerald-400"></i>
        <span>${a}</span>
      </li>
    `).join('') || '<li class="text-slate-500">No official apps registered.</li>';

    const pubsList = document.getElementById('modal-brand-pubs');
    pubsList.innerHTML = (brand.verified_publishers || []).map(p => `
      <li class="flex items-center gap-2 text-slate-300 font-mono text-xs">
        <i data-lucide="check-circle" class="w-3.5 h-3.5 text-emerald-400"></i>
        <span>${p}</span>
      </li>
    `).join('') || '<li class="text-slate-500">No verified publisher tags.</li>';

    UI.openModal('modal-brand-details');
    if (window.lucide) lucide.createIcons();
  },

  // ==========================================
  // 3. SOCIAL MEDIA THREAT MONITORING
  // ==========================================
  async renderSocialMonitoring() {
    const platform = document.getElementById('social-filter-platform')?.value || 'All';
    const severity = document.getElementById('social-filter-severity')?.value || 'All';
    const status = document.getElementById('social-filter-status')?.value || 'All';
    const search = document.getElementById('social-filter-search')?.value || '';
    
    let url = `/api/social-threats?platform=${encodeURIComponent(platform)}&severity=${encodeURIComponent(severity)}&status=${encodeURIComponent(status)}`;
    if (this.selectedBrand !== 'All Brands') url += `&brand_name=${encodeURIComponent(this.selectedBrand)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    try {
      const res = await fetch(url);
      if (res.ok) this.socialThreats = await res.json();
    } catch (e) {}

    const container = document.getElementById('social-threats-grid');
    if (!container) return;

    if (this.socialThreats.length === 0) {
      container.innerHTML = `<div class="col-span-3 text-center py-16 text-slate-500">No social threats match the selected filter criteria.</div>`;
      return;
    }

    container.innerHTML = this.socialThreats.map(t => `
      <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
        <div>
          <div class="flex items-start justify-between gap-3 mb-3">
            <div class="flex items-center gap-3">
              <img src="${t.profile_image_url || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=128&auto=format&fit=crop&q=80'}" class="w-11 h-11 rounded-full object-cover border-2 border-slate-700">
              <div>
                <h4 class="font-semibold text-slate-100 text-sm flex items-center gap-1.5">
                  ${t.account_name}
                  ${t.is_official_asset ? '<i data-lucide="check-check" class="w-4 h-4 text-emerald-400" title="Verified Whitelisted Asset"></i>' : ''}
                </h4>
                <div class="text-xs text-slate-400 font-mono">@${t.username}</div>
              </div>
            </div>
            ${UI.renderSeverityBadge(t.severity)}
          </div>

          <div class="flex items-center gap-2 mb-3 text-xs text-slate-300">
            ${UI.renderPlatformIcon(t.platform)}
            <span class="font-medium">${t.platform}</span>
            <span class="text-slate-600">&bull;</span>
            <span class="text-slate-400 font-mono text-[11px]">${t.similarity_pct}% similarity</span>
          </div>

          <div class="bg-slate-900/80 rounded-lg p-3 border border-slate-800 text-xs text-slate-300 mb-4 leading-relaxed">
            <div class="font-semibold text-cyan-400 mb-1 flex items-center gap-1">
              <i data-lucide="alert-triangle" class="w-3.5 h-3.5"></i> Detection Signals:
            </div>
            ${t.detection_reason}
          </div>

          <div class="mb-4">
            <div class="text-xs text-slate-400 mb-1 flex justify-between">
              <span>Risk Severity Index</span>
              <span class="font-mono text-slate-200">${t.risk_score}/100</span>
            </div>
            ${UI.renderRiskScore(t.risk_score)}
          </div>
        </div>

        <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
          <div class="flex items-center gap-1.5">
            <span class="text-slate-500">Status:</span>
            ${UI.renderStatusBadge(t.status)}
          </div>
          <div class="flex items-center gap-2">
            <a href="${t.profile_url}" target="_blank" class="px-2 py-1 rounded bg-slate-800 text-slate-300 hover:text-white border border-slate-700" title="Visit profile URL">
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
            </a>
            <button onclick="App.openThreatDetail('social', ${t.id})" class="px-2.5 py-1 rounded bg-blue-600/20 text-cyan-400 border border-blue-500/30 hover:bg-blue-600/30 font-medium">
              Actions
            </button>
          </div>
        </div>
      </div>
    `).join('');

    if (window.lucide) lucide.createIcons();
  },

  // ==========================================
  // 4. MOBILE APP STORE MONITORING
  // ==========================================
  async renderAppMonitoring() {
    const store = document.getElementById('apps-filter-store')?.value || 'All';
    const severity = document.getElementById('apps-filter-severity')?.value || 'All';
    const status = document.getElementById('apps-filter-status')?.value || 'All';
    const search = document.getElementById('apps-filter-search')?.value || '';

    let url = `/api/app-threats?store_name=${encodeURIComponent(store)}&severity=${encodeURIComponent(severity)}&status=${encodeURIComponent(status)}`;
    if (this.selectedBrand !== 'All Brands') url += `&brand_name=${encodeURIComponent(this.selectedBrand)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    try {
      const res = await fetch(url);
      if (res.ok) this.appThreats = await res.json();
    } catch (e) {}

    const container = document.getElementById('apps-threats-grid');
    if (!container) return;

    if (this.appThreats.length === 0) {
      container.innerHTML = `<div class="col-span-3 text-center py-16 text-slate-500">No suspicious mobile applications found matching criteria.</div>`;
      return;
    }

    container.innerHTML = this.appThreats.map(app => `
      <div class="glass-card rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
        <div>
          <div class="flex items-start justify-between gap-3 mb-3">
            <div class="flex items-center gap-3">
              <img src="${app.app_icon_url || 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=128&auto=format&fit=crop&q=80'}" class="w-12 h-12 rounded-xl object-cover border border-slate-700 shadow-md">
              <div>
                <h4 class="font-semibold text-slate-100 text-sm">${app.app_name}</h4>
                <div class="text-xs text-slate-400 truncate max-w-[180px]">${app.publisher}</div>
              </div>
            </div>
            ${UI.renderSeverityBadge(app.severity)}
          </div>

          <div class="flex items-center gap-2 mb-3 text-xs text-slate-300">
            ${UI.renderPlatformIcon(app.store_name)}
            <span class="font-medium">${app.store_name}</span>
            <span class="text-slate-600">&bull;</span>
            <span class="text-slate-400">Targeting: <b class="text-cyan-400">${app.brand_name}</b></span>
          </div>

          <!-- Multi-Signal Score Breakdown -->
          <div class="grid grid-cols-3 gap-2 bg-slate-900/80 rounded-lg p-2.5 border border-slate-800 mb-3 text-center text-xs">
            <div>
              <div class="text-[10px] text-slate-500 uppercase">Title</div>
              <div class="font-mono text-cyan-400 font-medium">${app.name_similarity_score}%</div>
            </div>
            <div>
              <div class="text-[10px] text-slate-500 uppercase">Logo</div>
              <div class="font-mono text-cyan-400 font-medium">${app.logo_similarity_score}%</div>
            </div>
            <div>
              <div class="text-[10px] text-slate-500 uppercase">Desc</div>
              <div class="font-mono text-cyan-400 font-medium">${app.description_similarity_score}%</div>
            </div>
          </div>

          <div class="mb-4">
            <div class="text-xs text-slate-400 mb-1 flex justify-between">
              <span>Overall Risk Score</span>
              <span class="font-mono text-slate-200">${app.risk_score}/100</span>
            </div>
            ${UI.renderRiskScore(app.risk_score)}
          </div>
        </div>

        <div class="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
          <div class="flex items-center gap-1.5">
            <span class="text-slate-500">Status:</span>
            ${UI.renderStatusBadge(app.status)}
          </div>
          <div class="flex items-center gap-2">
            <button onclick="App.openAppComparison(${app.id})" class="px-2.5 py-1 rounded bg-slate-800 text-slate-300 hover:text-white border border-slate-700 font-medium flex items-center gap-1">
              <i data-lucide="columns-2" class="w-3.5 h-3.5"></i> Compare
            </button>
            <button onclick="App.openThreatDetail('app', ${app.id})" class="px-2.5 py-1 rounded bg-blue-600/20 text-cyan-400 border border-blue-500/30 hover:bg-blue-600/30 font-medium">
              Actions
            </button>
          </div>
        </div>
      </div>
    `).join('');

    if (window.lucide) lucide.createIcons();
  },

  async openAppComparison(appId) {
    try {
      const res = await fetch(`/api/app-threats/${appId}/compare`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      
      const threat = data.threat;
      const brand = data.official_brand;
      const matrix = data.comparison_matrix;

      document.getElementById('compare-threat-name').textContent = threat.app_name;
      document.getElementById('compare-threat-publisher').textContent = threat.publisher;
      document.getElementById('compare-threat-icon').src = threat.app_icon_url;
      document.getElementById('compare-threat-store').textContent = threat.store_name;
      document.getElementById('compare-threat-risk').innerHTML = UI.renderRiskScore(threat.risk_score);
      
      document.getElementById('compare-official-brand').textContent = threat.brand_name;
      document.getElementById('compare-official-apps').textContent = (matrix.official_apps || []).join(', ') || 'Apex Mobile Banking';
      document.getElementById('compare-official-publishers').textContent = (matrix.official_publishers || []).join(', ') || 'Apex Financial Group LLC';
      document.getElementById('compare-official-icon').src = brand?.logo_url || threat.app_icon_url;

      document.getElementById('compare-matrix-title').textContent = matrix.title_match;
      document.getElementById('compare-matrix-logo').textContent = matrix.logo_imitation;
      document.getElementById('compare-matrix-pub').textContent = matrix.publisher_status;
      document.getElementById('compare-matrix-verdict').textContent = matrix.risk_verdict;

      UI.openModal('modal-app-compare');
    } catch (e) {
      UI.showToast('Could not load comparison data.', 'error');
    }
  },

  // ==========================================
  // 5. LOOK-ALIKE NAME RISK ANALYZER
  // ==========================================
  initAnalyzerView() {
    this.populateAnalyzerPresets();
  },

  async populateAnalyzerPresets() {
    const list = document.getElementById('analyzer-presets-list');
    if (!list) return;

    try {
      const res = await fetch('/api/analyze-name/presets');
      if (res.ok) {
        const presets = await res.json();
        list.innerHTML = presets.map(p => `
          <button onclick="App.applyAnalyzerPreset('${p.brand}', '${p.candidate}')" class="text-left p-3 rounded-lg bg-slate-900/80 hover:bg-slate-800/80 border border-slate-800 transition group">
            <div class="flex items-center justify-between text-xs font-mono font-medium text-cyan-400 group-hover:text-cyan-300">
              <span>${p.brand} &rarr; ${p.candidate}</span>
              <i data-lucide="arrow-right" class="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition"></i>
            </div>
            <div class="text-[11px] text-slate-400 mt-1">${p.desc}</div>
          </button>
        `).join('');
        if (window.lucide) lucide.createIcons();
      }
    } catch (e) {}
  },

  applyAnalyzerPreset(brand, candidate) {
    document.getElementById('analyzer-brand-input').value = brand;
    document.getElementById('analyzer-candidate-input').value = candidate;
    this.runNameAnalysis();
  },

  async runNameAnalysis() {
    const brandName = document.getElementById('analyzer-brand-input').value.trim();
    const candName = document.getElementById('analyzer-candidate-input').value.trim();
    const sensitivity = document.getElementById('analyzer-sensitivity').value;

    if (!brandName || !candName) {
      UI.showToast('Please enter both official brand name and candidate name.', 'error');
      return;
    }

    const btn = document.getElementById('analyzer-submit-btn');
    btn.innerHTML = `<span class="animate-spin inline-block mr-2">&#9696;</span> Analyzing RapidFuzz Vectors...`;
    btn.disabled = true;

    try {
      const res = await fetch('/api/analyze-name', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand_name: brandName,
          candidate_name: candName,
          sensitivity: sensitivity
        })
      });

      if (!res.ok) throw new Error();
      const data = await res.json();

      // Display Results
      document.getElementById('analyzer-results-card').classList.remove('hidden');
      document.getElementById('res-score-badge').innerHTML = UI.renderSeverityBadge(data.severity);
      document.getElementById('res-score-num').textContent = `${data.score}/100`;
      document.getElementById('res-score-bar').style.width = `${data.score}%`;
      
      let barCol = 'bg-blue-500';
      if (data.score >= 80) barCol = 'bg-red-500';
      else if (data.score >= 60) barCol = 'bg-orange-500';
      else if (data.score >= 30) barCol = 'bg-yellow-500';
      else if (data.score === 0) barCol = 'bg-emerald-500';
      document.getElementById('res-score-bar').className = `h-full rounded-full transition-all duration-700 ${barCol}`;

      document.getElementById('res-similarity-pct').textContent = `${data.name_similarity_pct}%`;
      document.getElementById('res-brand-norm').textContent = data.brand_normalized;
      document.getElementById('res-cand-norm').textContent = data.normalized_candidate || data.candidate_raw;

      // Substitutions
      const subContainer = document.getElementById('res-substitutions');
      if (data.substitutions_detected && data.substitutions_detected.length > 0) {
        subContainer.innerHTML = data.substitutions_detected.map(s => `
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-mono">
            '${s.original}' &rarr; '${s.replaces}' (${s.type})
          </span>
        `).join(' ');
      } else {
        subContainer.innerHTML = `<span class="text-xs text-slate-500">No leetspeak / homoglyphs detected</span>`;
      }

      // Keywords
      const kwContainer = document.getElementById('res-keywords');
      if (data.matched_keywords && data.matched_keywords.length > 0) {
        kwContainer.innerHTML = data.matched_keywords.map(kw => `
          <span class="inline-flex items-center px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/30 text-xs font-mono">
            +${kw}
          </span>
        `).join(' ');
      } else {
        kwContainer.innerHTML = `<span class="text-xs text-slate-500">No added deceptive keywords</span>`;
      }

      // Explanations list
      const expList = document.getElementById('res-explanations');
      expList.innerHTML = (data.explanations || []).map(exp => `
        <li class="flex items-start gap-2 text-xs text-slate-300">
          <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5"></i>
          <span>${exp}</span>
        </li>
      `).join('');

      // Formula breakdown
      const f = data.formula_breakdown || {};
      document.getElementById('res-formula').innerHTML = `
        <div class="grid grid-cols-4 gap-2 text-center text-xs font-mono">
          <div class="bg-slate-900/60 p-2 rounded border border-slate-800">
            <div class="text-[10px] text-slate-500">Fuzzy Base</div>
            <div class="text-slate-200">${f.fuzzy_lexical || 0} pts</div>
          </div>
          <div class="bg-slate-900/60 p-2 rounded border border-slate-800">
            <div class="text-[10px] text-slate-500">Substitutions</div>
            <div class="text-amber-400">+${f.substitution_penalty || 0} pts</div>
          </div>
          <div class="bg-slate-900/60 p-2 rounded border border-slate-800">
            <div class="text-[10px] text-slate-500">Risk Keywords</div>
            <div class="text-red-400">+${f.keyword_penalty || 0} pts</div>
          </div>
          <div class="bg-slate-900/60 p-2 rounded border border-slate-800">
            <div class="text-[10px] text-slate-500">Root Bonus</div>
            <div class="text-cyan-400">+${f.containment_bonus || 0} pts</div>
          </div>
        </div>
      `;

      UI.showToast(`Analysis complete: Score ${data.score} (${data.severity})`, 'info');
    } catch (e) {
      UI.showToast('Analysis request failed.', 'error');
    } finally {
      btn.innerHTML = `<i data-lucide="cpu" class="w-4 h-4"></i> Run AI Risk Analysis`;
      btn.disabled = false;
      if (window.lucide) lucide.createIcons();
    }
  },

  // ==========================================
  // 6. THREAT INVESTIGATION CENTER
  // ==========================================
  async renderThreatInvestigation() {
    const typeFilter = document.getElementById('threats-filter-type')?.value || '';
    const severity = document.getElementById('threats-filter-severity')?.value || 'All';
    const status = document.getElementById('threats-filter-status')?.value || 'All';
    const search = document.getElementById('threats-filter-search')?.value || '';

    let url = `/api/threats?threat_type=${encodeURIComponent(typeFilter)}&severity=${encodeURIComponent(severity)}&status=${encodeURIComponent(status)}`;
    if (this.selectedBrand !== 'All Brands') url += `&brand_name=${encodeURIComponent(this.selectedBrand)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    try {
      const res = await fetch(url);
      if (res.ok) this.unifiedThreats = await res.json();
    } catch (e) {}

    const tbody = document.getElementById('investigation-threats-tbody');
    if (!tbody) return;

    if (this.unifiedThreats.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="py-12 text-center text-slate-500">No threat incidents found matching search criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.unifiedThreats.map(t => `
      <tr class="border-b border-slate-800 hover:bg-slate-800/40 transition">
        <td class="py-3 px-4 font-mono text-xs text-slate-400">#DRS-${t.type.toUpperCase()}-${String(t.id).padStart(4, '0')}</td>
        <td class="py-3 px-4">
          <div class="flex items-center gap-3">
            <img src="${t.icon || 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=128&auto=format&fit=crop&q=80'}" class="w-8 h-8 rounded-lg object-cover border border-slate-700">
            <div>
              <div class="font-medium text-slate-200 text-sm">${t.display_title || t.account_name || t.app_name}</div>
              <div class="text-xs text-slate-400 font-mono">${t.brand_name}</div>
            </div>
          </div>
        </td>
        <td class="py-3 px-4">
          <div class="flex items-center gap-1.5 text-xs text-slate-300">
            ${UI.renderPlatformIcon(t.display_platform)}
            <span>${t.display_platform}</span>
          </div>
        </td>
        <td class="py-3 px-4">${UI.renderRiskScore(t.risk_score)}</td>
        <td class="py-3 px-4">${UI.renderSeverityBadge(t.severity)}</td>
        <td class="py-3 px-4">${UI.renderStatusBadge(t.status)}</td>
        <td class="py-3 px-4 text-xs text-slate-400 font-mono">${t.assigned_analyst || 'Unassigned'}</td>
        <td class="py-3 px-4 text-right">
          <button onclick="App.openThreatDetail('${t.type}', ${t.id})" class="px-3 py-1 text-xs font-medium rounded bg-blue-600/20 text-cyan-400 border border-blue-500/30 hover:bg-blue-600/30 transition flex items-center gap-1 ml-auto">
            <i data-lucide="shield-alert" class="w-3.5 h-3.5"></i> Investigate
          </button>
        </td>
      </tr>
    `).join('');

    if (window.lucide) lucide.createIcons();
  },

  async openThreatDetail(threatType, threatId) {
    try {
      const res = await fetch(`/api/threats/${threatType}/${threatId}`);
      if (!res.ok) throw new Error();
      const threat = await res.json();
      this.selectedThreat = threat;

      document.getElementById('modal-threat-id-title').textContent = `Incident #DRS-${threatType.toUpperCase()}-${String(threatId).padStart(4, '0')}`;
      document.getElementById('modal-threat-name').textContent = threat.account_name || threat.app_name;
      document.getElementById('modal-threat-platform').textContent = threat.platform || threat.store_name;
      document.getElementById('modal-threat-brand').textContent = threat.brand_name;
      document.getElementById('modal-threat-score').innerHTML = UI.renderRiskScore(threat.risk_score);
      document.getElementById('modal-threat-severity').innerHTML = UI.renderSeverityBadge(threat.severity);
      
      const reasons = Array.isArray(threat.detection_reasons) ? threat.detection_reasons.join(' ') : (threat.detection_reason || 'Impersonation detected.');
      document.getElementById('modal-threat-evidence').textContent = reasons;

      document.getElementById('threat-status-select').value = threat.status;
      document.getElementById('threat-analyst-input').value = threat.assigned_analyst || 'Sarah Chen';
      document.getElementById('threat-note-input').value = '';

      // Timeline render
      const timelineList = document.getElementById('modal-threat-timeline');
      timelineList.innerHTML = (threat.timeline || []).map(t => `
        <div class="relative pl-6 pb-4 border-l border-slate-700 last:border-0 last:pb-0">
          <div class="absolute -left-1.5 top-0 w-3 h-3 rounded-full bg-cyan-400 border-2 border-slate-900"></div>
          <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span class="font-medium text-slate-200">${t.author} &bull; ${t.action}</span>
            <span class="font-mono text-[11px]">${t.created_at}</span>
          </div>
          <div class="text-xs text-slate-300">${t.notes}</div>
        </div>
      `).join('') || `<div class="text-xs text-slate-500">No logged history.</div>`;

      UI.openModal('modal-threat-detail');
      if (window.lucide) lucide.createIcons();
    } catch (e) {
      UI.showToast('Could not open incident details.', 'error');
    }
  },

  async saveThreatUpdate() {
    if (!this.selectedThreat) return;
    const type = this.selectedThreat.type;
    const id = this.selectedThreat.id;
    const newStatus = document.getElementById('threat-status-select').value;
    const analyst = document.getElementById('threat-analyst-input').value.trim();
    const note = document.getElementById('threat-note-input').value.trim();

    try {
      const res = await fetch(`/api/threats/${type}/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          assigned_analyst: analyst,
          notes: note || `Updated incident status to ${newStatus}`
        })
      });

      if (res.ok) {
        UI.showToast('Incident updated successfully.', 'success');
        UI.closeModal('modal-threat-detail');
        this.refreshCurrentView();
      } else {
        UI.showToast('Failed to update incident.', 'error');
      }
    } catch (e) {
      UI.showToast('Network error while updating incident.', 'error');
    }
  },

  async generateTakedownNotice() {
    if (!this.selectedThreat) return;
    const type = this.selectedThreat.type;
    const id = this.selectedThreat.id;

    try {
      const res = await fetch(`/api/threats/${type}/${id}/takedown-notice`);
      if (res.ok) {
        const data = await res.json();
        document.getElementById('takedown-notice-text').value = data.notice_text;
        UI.openModal('modal-takedown-notice');
      }
    } catch (e) {
      UI.showToast('Could not generate takedown notice.', 'error');
    }
  },

  copyTakedownToClipboard() {
    const text = document.getElementById('takedown-notice-text').value;
    navigator.clipboard.writeText(text).then(() => {
      UI.showToast('Takedown notice copied to clipboard!', 'success');
    });
  },

  // ==========================================
  // 7. ACTIVE SCANNING RADAR SIMULATION
  // ==========================================
  async startScan(sourceType = 'all') {
    UI.openModal('modal-scanning-radar');
    const statusText = document.getElementById('radar-scan-status');
    const progressBar = document.getElementById('radar-scan-progress');
    const resultsContainer = document.getElementById('radar-scan-findings');
    
    statusText.textContent = `Initializing deep scan across authorized ${sourceType === 'apps' ? 'App Store' : 'Social Media'} vectors...`;
    progressBar.style.width = '15%';
    resultsContainer.innerHTML = '';

    setTimeout(async () => {
      progressBar.style.width = '55%';
      statusText.textContent = 'Normalizing strings & evaluating RapidFuzz multi-signal similarity...';

      try {
        const endpoint = sourceType === 'apps' ? '/api/scan/apps' : '/api/scan/social';
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ source_type: sourceType })
        });
        
        progressBar.style.width = '100%';
        statusText.textContent = 'Scan completed! Filtering against verified asset whitelist.';

        if (res.ok) {
          const data = await res.json();
          resultsContainer.innerHTML = (data.results || []).map(r => `
            <div class="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
              <div>
                <span class="font-medium text-slate-200">${r.account_name || r.app_name}</span>
                <span class="text-slate-500">(${r.brand_name})</span>
              </div>
              <div class="flex items-center gap-2">
                ${UI.renderRiskScore(r.risk_score)}
                ${UI.renderSeverityBadge(r.severity)}
              </div>
            </div>
          `).join('') || `<div class="text-xs text-slate-400 text-center py-2">No new threats discovered during this cycle.</div>`;

          UI.showToast(`Scan finished: ${data.new_threats_found} threat(s) detected.`, 'info');
          await this.loadInitialData();
          this.refreshCurrentView();
        }
      } catch (e) {
        statusText.textContent = 'Scan encountered an issue.';
      }
    }, 2200);
  },

  // ==========================================
  // 8. REPORTS AND ANALYTICS
  // ==========================================
  async renderReports() {
    try {
      const res = await fetch('/api/reports/summary');
      if (res.ok) {
        const rep = await res.json();
        
        document.getElementById('rep-total-threats').textContent = rep.stats.counters.potential_threats;
        document.getElementById('rep-critical-threats').textContent = rep.stats.counters.critical_threats;
        document.getElementById('rep-fp-rate').textContent = `${rep.false_positive_rate_pct}%`;
        document.getElementById('rep-resolved').textContent = rep.stats.counters.resolved_incidents;
        document.getElementById('rep-timestamp').textContent = rep.generated_at;

        // Recommendations
        const recList = document.getElementById('rep-recommendations');
        recList.innerHTML = rep.recommended_steps.map(s => `
          <li class="flex items-start gap-2 text-xs text-slate-300">
            <i data-lucide="shield-check" class="w-4 h-4 text-cyan-400 shrink-0 mt-0.5"></i>
            <span>${s}</span>
          </li>
        `).join('');

        // Top risk table
        const topTable = document.getElementById('rep-top-threats-tbody');
        topTable.innerHTML = rep.highest_risk_findings.map(t => `
          <tr class="border-b border-slate-800 text-xs">
            <td class="py-2.5 px-3 font-medium text-slate-200">${t.name}</td>
            <td class="py-2.5 px-3 text-slate-400">${t.brand_name}</td>
            <td class="py-2.5 px-3">${t.source}</td>
            <td class="py-2.5 px-3">${UI.renderRiskScore(t.risk_score)}</td>
            <td class="py-2.5 px-3">${UI.renderSeverityBadge(t.severity)}</td>
            <td class="py-2.5 px-3">${UI.renderStatusBadge(t.status)}</td>
          </tr>
        `).join('');

        if (window.lucide) lucide.createIcons();
      }
    } catch (e) {}
  },

  exportReport(format) {
    const base = window.API_BASE_URL || localStorage.getItem('drs_api_base_url') || '';
    const prefix = base ? base.replace(/\/+$/, '') : '';
    window.location.href = `${prefix}/api/reports/export?format=${format}`;
    UI.showToast(`Generating ${format.toUpperCase()} export...`, 'info');
  },

  printReport() {
    window.print();
  },

  // ==========================================
  // 9. AUTHENTICATION & DEMO MODE
  // ==========================================
  async handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (res.ok) {
        const data = await res.json();
        AppData.currentUser = data.user;
        localStorage.setItem('drs_user', JSON.stringify(data.user));
        this.updateUserBadge();
        UI.showToast(`Welcome back, ${data.user.username}!`, 'success');
        UI.closeModal('modal-auth');
        this.navigate('overview');
      } else {
        const err = await res.json();
        UI.showToast(err.detail || 'Login failed.', 'error');
      }
    } catch (e) {
      UI.showToast('Login network error.', 'error');
    }
  },

  async handleRegister(e) {
    e.preventDefault();
    const org = document.getElementById('reg-org').value.trim();
    const username = document.getElementById('reg-user').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-pass').value;

    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ organization: org, username, email, password })
      });

      if (res.ok) {
        const data = await res.json();
        AppData.currentUser = data.user;
        localStorage.setItem('drs_user', JSON.stringify(data.user));
        this.updateUserBadge();
        UI.showToast('Account registered successfully!', 'success');
        UI.closeModal('modal-auth');
        this.navigate('overview');
      } else {
        const err = await res.json();
        UI.showToast(err.detail || 'Registration failed.', 'error');
      }
    } catch (e) {
      UI.showToast('Registration error.', 'error');
    }
  },

  quickDemoLogin() {
    document.getElementById('login-email').value = 'analyst@apexfinancial.com';
    document.getElementById('login-password').value = 'demo123';
    document.getElementById('login-form').dispatchEvent(new Event('submit'));
  },

  async handleScanSingleSocial(e) {
    e.preventDefault();
    const form = e.target;
    const brandName = form.brand_name.value;
    const brand = this.brandsList.find(b => b.name === brandName) || this.brandsList[0];
    if (!brand) {
      UI.showToast('Please register a brand first.', 'error');
      return;
    }

    const payload = {
      brand_id: brand.id,
      account_name: form.account_name.value.trim(),
      username: form.username.value.trim().replace(/^@/, ''),
      platform: form.platform.value,
      profile_url: form.profile_url.value.trim(),
      profile_image_url: form.profile_image_url.value.trim()
    };

    try {
      const res = await fetch('/api/social-threats/scan-single', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        UI.showToast(`Evaluated: Risk Score ${data.risk_score} (${data.severity})`, 'info');
        UI.closeModal('modal-scan-single-social');
        form.reset();
        await this.loadInitialData();
        this.renderSocialMonitoring();
      } else {
        UI.showToast('Evaluation failed.', 'error');
      }
    } catch (err) {
      UI.showToast('Network error while evaluating social account.', 'error');
    }
  },

  async handleScanSingleApp(e) {
    e.preventDefault();
    const form = e.target;
    const brandName = form.brand_name.value;
    const brand = this.brandsList.find(b => b.name === brandName) || this.brandsList[0];
    if (!brand) {
      UI.showToast('Please register a brand first.', 'error');
      return;
    }

    const payload = {
      brand_id: brand.id,
      app_name: form.app_name.value.trim(),
      publisher: form.publisher.value.trim(),
      store_name: form.store_name.value,
      app_url: form.app_url.value.trim(),
      description: form.description.value.trim(),
      simulated_logo_similarity: parseFloat(form.logo_similarity.value) || 75.0
    };

    try {
      const res = await fetch('/api/app-threats/scan-single', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        UI.showToast(`App Evaluated: Risk Score ${data.risk_score} (${data.severity})`, 'info');
        UI.closeModal('modal-scan-single-app');
        form.reset();
        await this.loadInitialData();
        this.renderAppMonitoring();
      } else {
        UI.showToast('App evaluation failed.', 'error');
      }
    } catch (err) {
      UI.showToast('Network error while evaluating app.', 'error');
    }
  },

  logout() {
    localStorage.removeItem('drs_user');
    AppData.currentUser = { username: 'Guest Analyst', role: 'Viewer' };
    UI.showToast('Logged out.', 'info');
    this.navigate('landing');
  }
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
