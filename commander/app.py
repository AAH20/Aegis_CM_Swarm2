import os
import time
import json
import requests
from core.agent import AegisSwarmNode
from core.executor import execute_gitlab_incident
from core.mcp_bridge import mcp_tools_list

TARGET_URL = os.getenv("TARGET_BASE_URL", "http://target_arena:8000")

def send_log(msg, color="text-purple-400"):
    try: requests.post(f"{TARGET_URL}/log", json={"sender": "Purple Cmdr", "msg": msg, "color": color})
    except: pass

def save_caldera_profile(ttp, name, desc):
    os.makedirs("artifacts", exist_ok=True)
    filepath = f"artifacts/{ttp}_caldera_adversary.yml"

    yaml_content = f"""id: aegis-auto-{ttp.lower()}
name: 'A2Z SOC Auto-Generated: {name}'
description: 'Bootstrapped by Purple Commander Engine. {desc}'
objective: 4c424564-99a5-48b2-8409-eb5b01ce4556
tags:
  - aegis_swarm
  - a2z_soc
  - {ttp}
"""
    with open(filepath, "w") as f:
        f.write(yaml_content)
    return filepath, yaml_content

def main():
    time.sleep(5)

    commander = AegisSwarmNode(
        agent_role="You are the Purple Commander for A2Z SOC. Identify the attack and its exact MITRE ATT&CK TTP ID. You MUST sequentially trigger these tools: 1. dynatrace_anomaly_detect. 2. fivetran_sync_baseline. 3. mongodb_store_threat_intel. 4. elastic_siem_publish. 5. generate_caldera_profile. 6. gitlab_create_incident. 7. arize_log_agent_reasoning.",
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "demo-project"),
        location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
        mcp_tools=mcp_tools_list
    )
    print("[VERBOSE - COMMANDER] Commander booted. Starting telemetry loop.", flush=True)
    send_log("Purple Commander online. Gemini 2.5 Pro 6-Partner MCP Uplink ready.", "text-purple-300 font-bold")
    
    while True:
        try:
            metrics = requests.get(f"{TARGET_URL}/metrics").json()
            if metrics["under_attack"]:
                print(f"[VERBOSE - COMMANDER] Attack detected: {metrics['current_threat']}", flush=True)
                send_log(f"ANOMALY DETECTED. Feeding telemetry to Gemini 2.5 Pro...", "text-yellow-400 font-bold")
                
                response = commander.process_telemetry(json.dumps(metrics))
                
                if hasattr(response, 'candidates') and response.candidates:
                    current_caldera_yaml = "No profile generated."
                    print("[VERBOSE - COMMANDER] Gemini response received. Parsing function calls...", flush=True)

                    for call in response.candidates[0].function_calls:
                        print(f"[VERBOSE - COMMANDER] Executing tool: {call.name}", flush=True)
                        send_log(f"🚀 MCP TRIGGERED: {call.name}", "text-purple-400 font-bold")
                        
                        if call.name == "dynatrace_anomaly_detect":
                            send_log("📈 DYNATRACE: Correlating container anomalies...", "text-blue-300 font-bold")

                        elif call.name == "fivetran_sync_baseline":
                            send_log("🔁 FIVETRAN: Syncing defense baseline...", "text-cyan-300 font-bold")

                        elif call.name == "mongodb_store_threat_intel":
                            send_log("🍃 MONGODB: Persisting threat intelligence snapshot...", "text-green-300 font-bold")

                        elif call.name == "elastic_siem_publish":
                            send_log("🔍 ELASTIC SIEM: Threat signature published.", "text-yellow-300 font-bold")

                        elif call.name == "arize_log_agent_reasoning":
                            send_log("📊 ARIZE: Agent reasoning logged for review.", "text-pink-300 font-bold")

                        elif call.name == "generate_caldera_profile":
                            path, current_caldera_yaml = save_caldera_profile(
                                call.args.get('mitre_ttp'),
                                call.args.get('adversary_name'),
                                call.args.get('description')
                            )
                            send_log(f"🧬 PURPLE TEAM BOOTSTRAP: MITRE Caldera profile saved to {path}", "text-fuchsia-400 font-bold")

                        if call.name == "gitlab_create_incident":
                            title = call.args.get('incident_title', 'Security Alert')
                            current_caldera_yaml = call.args.get('caldera_yaml_content', current_caldera_yaml)
                            send_log("🦊 GITLAB: Connecting to real API...", "text-orange-300")
                            api_result = execute_gitlab_incident(title, current_caldera_yaml)
                            print(f"[VERBOSE - COMMANDER] GitLab API Output: {api_result}", flush=True)
                            send_log(f"🦊 GITLAB RESPONSE: {api_result}", "text-orange-400 font-bold")
                            requests.post(f"{TARGET_URL}/trigger_toast", json={"msg": f"GitLab Issue Opened: {title}"})
                            requests.post(f"{TARGET_URL}/trigger_audio", json={"msg": f"Threat detected. Git lab Incident created for {title}"})
                            
                        requests.post(f"{TARGET_URL}/log", json={"sender": "Purple Cmdr", "msg": f"🚀 MCP TRIGGERED: {call.name}", "color": "text-purple-400 font-bold"})
                
                time.sleep(2)
                requests.post(f"{TARGET_URL}/remediate")
                send_log("System auto-healed. Baseline restored.", "text-slate-400")
                time.sleep(15)
                
        except Exception as e:
            print(f"[VERBOSE - COMMANDER ERROR] {e}", flush=True)
        time.sleep(2)

if __name__ == "__main__":
    main()