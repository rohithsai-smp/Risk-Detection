/**
 * Digital Risk Shield - Reusable UI Components & Helpers
 */

const UI = {
  renderSeverityBadge(severity) {
    const s = (severity || 'Low').toLowerCase();
    let badgeClass = 'badge-low';
    let dotColor = 'bg-blue-400';
    
    if (s === 'critical') {
      badgeClass = 'badge-critical';
      dotColor = 'bg-red-500 animate-pulse';
    } else if (s === 'high') {
      badgeClass = 'badge-high';
      dotColor = 'bg-orange-500';
    } else if (s === 'medium') {
      badgeClass = 'badge-medium';
      dotColor = 'bg-yellow-400';
    } else if (s === 'safe') {
      badgeClass = 'badge-safe';
      dotColor = 'bg-emerald-400';
    }
    
    return `
      <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${badgeClass}">
        <span class="w-1.5 h-1.5 rounded-full ${dotColor}"></span>
        ${severity}
      </span>
    `;
  },

  renderRiskScore(score) {
    const num = Math.min(Math.max(parseInt(score) || 0, 0), 100);
    let barColor = 'bg-blue-500';
    let textColor = 'text-blue-400';
    
    if (num >= 80) {
      barColor = 'bg-red-500';
      textColor = 'text-red-400 font-bold';
    } else if (num >= 60) {
      barColor = 'bg-orange-500';
      textColor = 'text-orange-400 font-semibold';
    } else if (num >= 30) {
      barColor = 'bg-yellow-500';
      textColor = 'text-yellow-400';
    } else if (num === 0) {
      barColor = 'bg-emerald-500';
      textColor = 'text-emerald-400';
    }

    return `
      <div class="flex items-center gap-2 min-w-[120px]">
        <div class="w-12 text-right text-xs font-mono ${textColor}">${num}/100</div>
        <div class="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden border border-slate-700/60">
          <div class="${barColor} h-full rounded-full transition-all duration-500" style="width: ${num}%"></div>
        </div>
      </div>
    `;
  },

  renderStatusBadge(status) {
    const st = status || 'New';
    const map = {
      'New': 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30',
      'Under Investigation': 'bg-amber-500/10 text-amber-400 border border-amber-500/30',
      'Confirmed Threat': 'bg-red-500/10 text-red-400 border border-red-500/30',
      'False Positive': 'bg-slate-700/50 text-slate-300 border border-slate-600',
      'Resolved': 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
    };
    const cls = map[st] || 'bg-slate-800 text-slate-300 border border-slate-700';
    return `<span class="px-2.5 py-1 rounded text-xs font-medium ${cls}">${st}</span>`;
  },

  renderPlatformIcon(platform) {
    const p = (platform || '').toLowerCase();
    if (p.includes('twitter') || p.includes('x')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-sky-500/20 text-sky-400"><i data-lucide="twitter" class="w-4 h-4"></i></span>`;
    } else if (p.includes('instagram')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-pink-500/20 text-pink-400"><i data-lucide="instagram" class="w-4 h-4"></i></span>`;
    } else if (p.includes('facebook')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-blue-600/20 text-blue-400"><i data-lucide="facebook" class="w-4 h-4"></i></span>`;
    } else if (p.includes('linkedin')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-indigo-500/20 text-indigo-400"><i data-lucide="linkedin" class="w-4 h-4"></i></span>`;
    } else if (p.includes('youtube')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-red-600/20 text-red-400"><i data-lucide="youtube" class="w-4 h-4"></i></span>`;
    } else if (p.includes('telegram')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-cyan-500/20 text-cyan-400"><i data-lucide="send" class="w-4 h-4"></i></span>`;
    } else if (p.includes('play')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-emerald-500/20 text-emerald-400"><i data-lucide="play" class="w-4 h-4"></i></span>`;
    } else if (p.includes('apple') || p.includes('ios')) {
      return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-slate-300/20 text-slate-200"><i data-lucide="apple" class="w-4 h-4"></i></span>`;
    }
    return `<span class="inline-flex items-center justify-center w-7 h-7 rounded-lg bg-purple-500/20 text-purple-400"><i data-lucide="globe" class="w-4 h-4"></i></span>`;
  },

  showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm';
      document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    const borderCol = type === 'success' ? 'border-emerald-500' : (type === 'error' ? 'border-red-500' : 'border-cyan-500');
    toast.className = `glass-panel ${borderCol} p-3 rounded-lg shadow-xl text-sm flex items-center justify-between gap-3 text-slate-100 transition-all duration-300 transform translate-y-2 opacity-0`;
    toast.innerHTML = `
      <div class="flex items-center gap-2.5">
        <span class="w-2 h-2 rounded-full ${type === 'success' ? 'bg-emerald-400' : (type === 'error' ? 'bg-red-400' : 'bg-cyan-400')}"></span>
        <span>${message}</span>
      </div>
      <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white">&times;</button>
    `;
    
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);
    
    setTimeout(() => {
      toast.classList.add('opacity-0');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      if (window.lucide) lucide.createIcons();
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }
  }
};
