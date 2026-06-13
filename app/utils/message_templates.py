"""
Semantic template registry utilizing secure standard HTML markup tags.
Supported HTML elements natively by Telegram: <b>, <i>, <a>, <code>, <pre>.
"""

TEMPLATES = {
    "RAIN_HOLIDAY": (
        "🌧️ <b>🚨 SCHOOL & COLLEGE HOLIDAY ALERT</b> 🌧️\n"
        "----------------------------------------\n"
        "📍 <b>District:</b> {district}\n"
        "📅 <b color='red'>Affected Date:</b> {date}\n"
        "📢 <b>Announcement:</b> {title}\n\n"
        "📝 <b>Details:</b> {content}\n\n"
        "🔗 <i>Source Reference: <a href='{url}'>Official Order</a></i>\n"
        "⚠️ #TN_RainHoliday #TamilNadu"
    ),
    "GOVERNMENT_HOLIDAY": (
        "🏛️ <b>PUBLIC HOLIDAY ANNOUNCEMENT</b> 🏛️\n"
        "----------------------------------------\n"
        "📍 <b>Scope:</b> {district} (Statewide/Local)\n"
        "📅 <b>Date:</b> {date}\n"
        "📣 <b>Occasion:</b> {title}\n\n"
        "📝 <b>Briefing:</b> {content}\n\n"
        "🔗 <i>Source: <a href='{url}'>Government Gazette</a></i>\n"
        "📌 #TNGovtHoliday #PublicHoliday"
    ),
    "WEATHER_ALERT": (
        "⚡ <b>METEOROLOGICAL WARNING (IMD)</b> ⚡\n"
        "----------------------------------------\n"
        "📍 <b>Region:</b> {district}\n"
        "📅 <b>Validity:</b> {date}\n"
        "🚨 <b>Alert Level:</b> {title}\n\n"
        "📝 <b>Impact Assessment:</b> {content}\n\n"
        "📡 <i>Data Source: <a href='{url}'>IMD / Weather Hub</a></i>\n"
        "⚠️ #TNWeather #SafetyFirst"
    ),
    "CYCLONE_ALERT": (
        "🌀 <b>CRITICAL CYCLONE TRACKING NOTICE</b> 🌀\n"
        "----------------------------------------\n"
        "📍 <b>Target Zones:</b> {district}\n"
        "📅 <b>Timeline:</b> {date}\n"
        "⚠️ <b>System Level:</b> {title}\n\n"
        "📝 <b>Directives:</b> {content}\n\n"
        "🌊 <i>Live Tracker: <a href='{url}'>Disaster Management Portal</a></i>\n"
        "🚨 #CycloneAlert #TNDisasterMgmt"
    ),
    "FLOOD_ALERT": (
        "🌊 <b>INUNDATION & FLOOD INVENTORY WARN</b> 🌊\n"
        "----------------------------------------\n"
        "📍 <b>Locations:</b> {district}\n"
        "📅 <b>Issued Date:</b> {date}\n"
        "🚨 <b>Risk Index:</b> {title}\n\n"
        "📝 <b>Emergency Scope:</b> {content}\n\n"
        "🛠️ <i>Helpline Info: <a href='{url}'>Emergency Links</a></i>\n"
        "🚫 #TNFloodAlert #RescueInfo"
    ),
    "DAM_RELEASE": (
        "🎚️ <b>DAM SURGE DISCHARGE NOTICE</b> 🎚️\n"
        "----------------------------------------\n"
        "📍 <b>River Basin/District:</b> {district}\n"
        "📅 <b>Action Date:</b> {date}\n"
        "🌊 <b>Inflow Rate:</b> {title}\n\n"
        "📝 <b>Downstream Warnings:</b> {content}\n\n"
        "📊 <i>Live Reservoir Stats: <a href='{url}'>PWD Metrics Portal</a></i>\n"
        "⚠️ #DamDischarge #WaterLevelAlert"
    ),
    "ROAD_CLOSURE": (
        "🚧 <b>TRAFFIC ROUTING & ROAD CLOSURE</b> 🚧\n"
        "----------------------------------------\n"
        "📍 <b>Jurisdiction:</b> {district}\n"
        "📅 <b>Active Window:</b> {date}\n"
        "🚗 <b>Incident/Reason:</b> {title}\n\n"
        "🗺️ <b>Diversion Routes:</b> {content}\n\n"
        "🚨 <i>Traffic Police Feed: <a href='{url}'>Official Status</a></i>\n"
        "📌 #TNTraffic #RoadBlock"
    ),
    "TRANSPORT_ALERT": (
        "🚍 <b>TRANSIT NETWORK TRANSITION NOTIFICATION</b> 🚍\n"
        "----------------------------------------\n"
        "📍 <b>Coverage:</b> {district}\n"
        "📅 <b>Operational Date:</b> {date}\n"
        "🚂 <b>Service Disruption:</b> {title}\n\n"
        "📝 <b>Alternative Transit Methods:</b> {content}\n\n"
        "🎟️ <i>Carrier Notice: <a href='{url}'>TNSTC / Southern Railway</a></i>\n"
        "📌 #TNTransport #TransitAlert"
    ),
    "POWER_ALERT": (
        "🔌 <b>TANGEDCO POWER SHUTDOWN MATRIX</b> 🔌\n"
        "----------------------------------------\n"
        "📍 <b>Substation Feeders:</b> {district}\n"
        "📅 <b>Maintenance Window:</b> {date}\n"
        "⏰ <b>Interruption Scope:</b> {title}\n\n"
        "📝 <b>Impacted Localities:</b> {content}\n\n"
        "⚡ <i>Schedule Feed: <a href='{url}'>TANGEDCO Portal</a></i>\n"
        "💡 #TNEB #PowerShutdown"
    ),
    "EMERGENCY_ALERT": (
        "🚨 <b>🆘 CRITICAL ADVISORY LEVEL 🆘</b> 🚨\n"
        "----------------------------------------\n"
        "📍 <b>Scope Zone:</b> {district}\n"
        "📅 <b>Time Anchor:</b> {date}\n"
        "🔥 <b>Threat:</b> {title}\n\n"
        "❗ <b>Actionable Instructions:</b> {content}\n\n"
        "📞 <i>Control Room Access: <a href='{url}'>Click for Assistance</a></i>\n"
        "🛑 #TNEmergency #ImmediateAction"
    ),
    "EXAM_NOTIFICATION": (
        "🎓 <b>OFFICIAL ACADEMIC EXAM STATUS</b> 🎓\n"
        "----------------------------------------\n"
        "📍 <b>Board/University:</b> {district}\n"
        "📅 <b color='blue'>Timeline Details:</b> {date}\n"
        "📝 <b>Postponement/Schedule:</b> {title}\n\n"
        "📝 <b>Affected Frameworks:</b> {content}\n\n"
        "🔗 <i>Notification Sheet: <a href='{url}'>Circular Download</a></i>\n"
        "📌 #TNExams #EducationAlert"
    ),
    "TOMORROW_HOLIDAY_PROBABILITY": (
        "🤖 <b>HOLIDAY PROBABILITY INDEX MODEL</b> 🤖\n"
        "----------------------------------------\n"
        "📍 <b>District:</b> {district}\n"
        "📅 <b>Evaluated Date:</b> {date}\n"
        "📊 <b>Confidence Rating:</b> {title}\n\n"
        "🔮 <b>AI Analytical Inference:</b> {content}\n\n"
        "📈 <i>Detailed Trend Models: <a href='{url}'>Prediction Engine</a></i>\n"
        "🤖 #AIPrediction #TNHolidayTrend"
    )
}