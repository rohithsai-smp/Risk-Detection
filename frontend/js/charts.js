/**
 * Digital Risk Shield - Chart.js Visualizations
 * Dark cybersecurity operations styling
 */

const Charts = {
  instances: {},

  initAll(chartData) {
    if (!window.Chart) return;
    
    // Set global Chart defaults for dark SOC theme
    Chart.defaults.color = '#94A3B8';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.scale.grid.color = 'rgba(51, 65, 85, 0.3)';
    Chart.defaults.plugins.tooltip.backgroundColor = '#1E293B';
    Chart.defaults.plugins.tooltip.borderColor = '#334155';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.titleColor = '#F8FAFC';
    Chart.defaults.plugins.tooltip.bodyColor = '#CBD5E1';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;

    this.renderTrendChart(chartData.timeline_trend);
    this.renderPlatformChart(chartData.platforms);
    this.renderSeverityChart(chartData.severities);
    this.renderStatusChart(chartData.status_breakdown);
    this.renderSourceComparisonChart(chartData.source_comparison);
  },

  renderTrendChart(trendData) {
    const ctx = document.getElementById('chart-trend');
    if (!ctx) return;
    if (this.instances.trend) this.instances.trend.destroy();

    const labels = (trendData || []).map(d => d.day);
    const threats = (trendData || []).map(d => d.threats);
    const resolved = (trendData || []).map(d => d.resolved);

    this.instances.trend = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Detected Threats',
            data: threats,
            borderColor: '#EF4444',
            backgroundColor: 'rgba(239, 68, 68, 0.12)',
            borderWidth: 2,
            tension: 0.35,
            fill: true,
            pointBackgroundColor: '#EF4444',
            pointRadius: 4
          },
          {
            label: 'Resolved Incidents',
            data: resolved,
            borderColor: '#22C55E',
            backgroundColor: 'rgba(34, 197, 94, 0.08)',
            borderWidth: 2,
            tension: 0.35,
            fill: true,
            pointBackgroundColor: '#22C55E',
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, usePointStyle: true }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  },

  renderPlatformChart(platformData) {
    const ctx = document.getElementById('chart-platforms');
    if (!ctx) return;
    if (this.instances.platforms) this.instances.platforms.destroy();

    const labels = Object.keys(platformData || {});
    const counts = Object.values(platformData || {});

    this.instances.platforms = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Impersonation Threats',
          data: counts,
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(236, 72, 153, 0.8)',
            'rgba(99, 102, 241, 0.8)',
            'rgba(34, 211, 238, 0.8)',
            'rgba(168, 85, 247, 0.8)'
          ],
          borderRadius: 6,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  },

  renderSeverityChart(severityData) {
    const ctx = document.getElementById('chart-severity');
    if (!ctx) return;
    if (this.instances.severity) this.instances.severity.destroy();

    const data = severityData || { Critical: 4, High: 3, Medium: 2, Low: 0, Safe: 2 };

    this.instances.severity = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Critical', 'High', 'Medium', 'Low', 'Safe'],
        datasets: [{
          data: [
            data.Critical || 0,
            data.High || 0,
            data.Medium || 0,
            data.Low || 0,
            data.Safe || 0
          ],
          backgroundColor: [
            '#EF4444',
            '#F97316',
            '#EAB308',
            '#3B82F6',
            '#22C55E'
          ],
          borderColor: '#111827',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'right',
            labels: { boxWidth: 12, usePointStyle: true }
          }
        }
      }
    });
  },

  renderStatusChart(statusData) {
    const ctx = document.getElementById('chart-status');
    if (!ctx) return;
    if (this.instances.status) this.instances.status.destroy();

    const labels = Object.keys(statusData || {});
    const counts = Object.values(statusData || {});

    this.instances.status = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: [
            '#22D3EE',
            '#F59E0B',
            '#EF4444',
            '#10B981',
            '#64748B'
          ],
          borderColor: '#111827',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, usePointStyle: true }
          }
        }
      }
    });
  },

  renderSourceComparisonChart(sourceData) {
    const ctx = document.getElementById('chart-source-comparison');
    if (!ctx) return;
    if (this.instances.source) this.instances.source.destroy();

    const labels = Object.keys(sourceData || {});
    const counts = Object.values(sourceData || {});

    this.instances.source = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: ['#3B82F6', '#8B5CF6'],
          borderColor: '#111827',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 10, usePointStyle: true }
          }
        }
      }
    });
  }
};
