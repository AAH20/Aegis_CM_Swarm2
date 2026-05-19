from vertexai.generative_models import FunctionDeclaration

# 1. DYNATRACE MCP
dynatrace_anomaly_detect = FunctionDeclaration(
    name="dynatrace_anomaly_detect",
    description="Fetches CPU, memory, and network anomaly metrics from Dynatrace for root cause analysis.",
    parameters={"type": "object", "properties": {"container_name": {"type": "string"}}, "required": ["container_name"]}
)

# 2. ELASTIC MCP
elastic_siem_publish = FunctionDeclaration(
    name="elastic_siem_publish",
    description="Publishes a verified threat signature and MITRE ATT&CK mapping to the Elastic Security SIEM.",
    parameters={"type": "object", "properties": {"threat_level": {"type": "string"}, "mitre_ttp": {"type": "string"}}, "required": ["threat_level", "mitre_ttp"]}
)

# 3. FIVETRAN MCP
fivetran_sync_baseline = FunctionDeclaration(
    name="fivetran_sync_baseline",
    description="Synchronizes the latest defensive telemetry baseline through Fivetran for the SOC pipeline.",
    parameters={"type": "object", "properties": {"baseline_name": {"type": "string"}}, "required": ["baseline_name"]}
)

# 4. MONGODB MCP
mongodb_store_threat_intel = FunctionDeclaration(
    name="mongodb_store_threat_intel",
    description="Stores threat intelligence records and incident context in MongoDB for later analysis.",
    parameters={"type": "object", "properties": {"incident_id": {"type": "string"}, "ioc_summary": {"type": "string"}}, "required": ["incident_id", "ioc_summary"]}
)

# 5. GITLAB MCP
gitlab_create_incident = FunctionDeclaration(
    name="gitlab_create_incident",
    description="Opens an urgent Security Incident in GitLab and commits the MITRE Caldera YAML profile to the Purple Team repository.",
    parameters={
        "type": "object",
        "properties": {
            "incident_title": {"type": "string", "description": "Title of the GitLab issue"},
            "caldera_yaml_content": {"type": "string", "description": "The raw YAML content for the Caldera adversary profile"}
        },
        "required": ["incident_title", "caldera_yaml_content"]
    }
)

# 6. ARIZE MCP
arize_log_agent_reasoning = FunctionDeclaration(
    name="arize_log_agent_reasoning",
    description="Logs agent reasoning, decisions, and tool execution traces to Arize for observability.",
    parameters={"type": "object", "properties": {"run_id": {"type": "string"}, "summary": {"type": "string"}}, "required": ["run_id", "summary"]}
)

# 7. MITRE CALDERA LOCAL GENERATOR
generate_caldera_profile = FunctionDeclaration(
    name="generate_caldera_profile",
    description="Generates a MITRE Caldera adversary profile YAML file for Purple Team tabletop exercises.",
    parameters={
        "type": "object",
        "properties": {
            "mitre_ttp": {"type": "string", "description": "The exact MITRE ATT&CK TTP ID (e.g., T1110)"},
            "adversary_name": {"type": "string", "description": "A cool name for the adversary"},
            "description": {"type": "string", "description": "Technical description of the attack"}
        },
        "required": ["mitre_ttp", "adversary_name", "description"]
    }
)

# Export a raw Python list so callers can pass it directly to the Vertex wrapper
mcp_tools_list = [
    dynatrace_anomaly_detect,
    elastic_siem_publish,
    fivetran_sync_baseline,
    mongodb_store_threat_intel,
    gitlab_create_incident,
    arize_log_agent_reasoning,
    generate_caldera_profile,
]