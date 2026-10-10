/**
 * Digital Risk Shield - Client State & Data Defaults
 */

const AppData = {
  activeBrand: "All Brands",
  brands: [],
  socialThreats: [],
  appThreats: [],
  unifiedThreats: [],
  currentUser: {
    username: "soc_analyst",
    email: "analyst@apexfinancial.com",
    role: "Lead Risk Analyst",
    organization: "Apex Financial SOC Team"
  },
  stats: {
    counters: {
      total_brands: 3,
      social_analyzed: 55,
      apps_analyzed: 36,
      potential_threats: 9,
      critical_threats: 4,
      resolved_incidents: 2
    },
    charts: {
      platforms: {
        "X (Twitter)": 2,
        "Instagram": 2,
        "LinkedIn": 1,
        "Facebook": 1,
        "Telegram": 1
      },
      severities: {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 0,
        "Safe": 2
      },
      source_comparison: {
        "Social Media": 5,
        "Mobile App Stores": 3
      },
      status_breakdown: {
        "New": 3,
        "Under Investigation": 4,
        "Confirmed Threat": 2,
        "Resolved": 2
      },
      timeline_trend: [
        { day: "Mon", threats: 4, resolved: 2 },
        { day: "Tue", threats: 7, resolved: 3 },
        { day: "Wed", threats: 5, resolved: 4 },
        { day: "Thu", threats: 12, resolved: 6 },
        { day: "Fri", threats: 8, resolved: 5 },
        { day: "Sat", threats: 11, resolved: 7 },
        { day: "Sun", threats: 9, resolved: 2 }
      ]
    }
  }
};
