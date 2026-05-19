from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI(title=os.getenv("APP_NAME", "Aegis_Arena"))

system_state = {
    "cpu_percent": 15.0, "disk_io_mbps": 5.0, "network_rps": 12,
    "auth_failures": 0, "snort_alerts": 0, "waf_blocks": 0, "syscall_alerts": 0,
    "under_attack": False, "current_threat": "None",
    "log_id_counter": 0, "mcp_id_counter": 0,
    "logs": [{"id": 0, "sender": "System", "msg": "A2Z SOC Enterprise GUI Initialized", "color": "text-slate-500"}],
    "mcp_logs": [], 
    "toast_queue": [], 
    "audio_queue": [], 
    "simulation_started": False
}

class LogEntry(BaseModel):
    sender: str
    msg: str
    color: str = "text-slate-300"

class ToastMsg(BaseModel):
    msg: str

class AudioMsg(BaseModel):
    msg: str

class AttackPayload(BaseModel):
    attack_type: str

@app.post("/start_simulation")
def start_simulation():
    print("[VERBOSE - GUI] Simulation Started by User", flush=True)
    system_state["simulation_started"] = True
    return {"status": "started"}

@app.get("/simulation_status")
def simulation_status():
    return {"started": system_state["simulation_started"]}

@app.post("/log")
def add_log(entry: LogEntry):
    print(f"[GUI LOG] [{entry.sender}] {entry.msg}", flush=True)
    system_state["log_id_counter"] += 1
    system_state["logs"].append({"id": system_state["log_id_counter"], "sender": entry.sender, "msg": entry.msg, "color": entry.color})
    if len(system_state["logs"]) > 200: system_state["logs"].pop(0)
    
    keywords = ["MCP TRIGGERED", "GITLAB", "ELASTIC", "DYNATRACE", "FIVETRAN", "MONGODB", "ARIZE", "PURPLE TEAM BOOTSTRAP"]
    if any(keyword in entry.msg for keyword in keywords):
        system_state["mcp_id_counter"] += 1
        system_state["mcp_logs"].append({"id": system_state["mcp_id_counter"], "sender": entry.sender, "msg": entry.msg, "color": entry.color})
        if len(system_state["mcp_logs"]) > 20: system_state["mcp_logs"].pop(0)
        
    return {"status": "ok"}

@app.post("/trigger_toast")
def trigger_toast(data: ToastMsg):
    print(f"[VERBOSE - GUI] Queueing Toast: {data.msg}", flush=True)
    system_state["toast_queue"].append(data.msg)
    return {"status": "Toast queued"}

@app.post("/trigger_audio")
def trigger_audio(data: AudioMsg):
    print(f"[VERBOSE - GUI] Queueing Audio: {data.msg}", flush=True)
    system_state["audio_queue"].append(data.msg)
    return {"status": "Audio queued"}

@app.post("/launch_attack")
def launch_attack(payload: AttackPayload):
    print(f"[VERBOSE - GUI] Attack Executed: {payload.attack_type.upper()}", flush=True)
    system_state["under_attack"] = True
    system_state["current_threat"] = payload.attack_type.upper()
    if payload.attack_type == "nmap": system_state["snort_alerts"] = 450
    elif payload.attack_type == "sqli": system_state["waf_blocks"] = 1205
    elif payload.attack_type == "brute_force": system_state["auth_failures"] = 8500
    elif payload.attack_type == "crypto": system_state["cpu_percent"] = 100.0
    elif payload.attack_type == "ransomware": system_state["disk_io_mbps"] = 4500.0; system_state["cpu_percent"] = 85.0
    elif payload.attack_type == "ddos": system_state["network_rps"] = 25000; system_state["cpu_percent"] = 98.0
    elif payload.attack_type == "container_escape": system_state["syscall_alerts"] = 12
    elif payload.attack_type == "lateral_movement": system_state["snort_alerts"] = 890; system_state["network_rps"] = 300
    return {"status": "Attack launched"}

@app.post("/remediate")
def remediate():
    print("[VERBOSE - GUI] Remediation endpoint hit. Healing system.", flush=True)
    system_state.update({
        "cpu_percent": 15.0, "disk_io_mbps": 5.0, "network_rps": 12,
        "auth_failures": 0, "snort_alerts": 0, "waf_blocks": 0, "syscall_alerts": 0,
        "under_attack": False, "current_threat": "None"
    })
    return {"status": "System Healed"}

@app.get("/api/state")
def get_state():
    toasts = list(system_state["toast_queue"])
    audios = list(system_state["audio_queue"])
    system_state["toast_queue"].clear()
    system_state["audio_queue"].clear()

    return {**system_state, "toast_queue": toasts, "audio_queue": audios}

@app.get("/metrics")
def get_metrics():
    return system_state

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>A2Z SOC | Purple Commander</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { background-color: #020617; color: #f8fafc; font-family: ui-sans-serif, system-ui, sans-serif; 
                   background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px); background-size: 20px 20px; }
            html, body { height: 100%; }
            body { overflow: hidden; }
            .glow-red { box-shadow: 0 0 25px rgba(239, 68, 68, 0.3); border-color: #ef4444; }
            .glow-blue { box-shadow: 0 0 25px rgba(59, 130, 246, 0.3); border-color: #3b82f6; }
            .glow-purple { box-shadow: 0 0 30px rgba(168, 85, 247, 0.4); border-color: #a855f7; }
            .card { background-color: rgba(15, 23, 42, 0.8); backdrop-filter: blur(12px); border: 1px solid #1e293b; border-radius: 0.75rem; padding: 1rem; transition: all 0.3s; min-width: 0; min-height: 0; }
            .log-container { font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.85rem; overflow-y: auto; overscroll-behavior: contain; scrollbar-width: thin; }
            .log-container::-webkit-scrollbar { width: 10px; }
            .log-container::-webkit-scrollbar-track { background: #0f172a; border-radius: 999px; }
            .log-container::-webkit-scrollbar-thumb { background: #334155; border-radius: 999px; }
            .panel-scroll { overflow-y: auto; overscroll-behavior: contain; scrollbar-width: thin; }
            .panel-scroll::-webkit-scrollbar { width: 10px; }
            .panel-scroll::-webkit-scrollbar-track { background: #0f172a; border-radius: 999px; }
            .panel-scroll::-webkit-scrollbar-thumb { background: #334155; border-radius: 999px; }
            .mcp-item { background: linear-gradient(90deg, rgba(168,85,247,0.1) 0%, rgba(15,23,42,0) 100%); border-left: 3px solid #a855f7; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 0 0.5rem 0.5rem 0;}
            .sensor { background-color: rgba(2, 6, 23, 0.5); border: 1px solid #1e293b; border-radius: 0.5rem; padding: 0.75rem; text-align: center; min-width: 0; }
            .dashboard-shell { height: 100%; min-height: 0; }
            .dashboard-grid { min-height: 0; }
        </style>
    </head>
    <body class="h-screen p-3 sm:p-4 lg:p-6 flex flex-col relative">
        
        <div id="toast-container" class="fixed top-4 right-4 sm:top-6 sm:right-6 z-50 flex flex-col gap-3 max-w-[calc(100vw-2rem)] sm:max-w-sm"></div>

        <div id="audio-overlay" class="absolute inset-0 bg-slate-950/95 z-50 flex items-center justify-center backdrop-blur-md">
            <div class="text-center card glow-purple max-w-lg">
                <h2 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-emerald-400 mb-2">A2Z SOC Enterprise</h2>
                <p class="text-slate-400 mb-6">Autonomous Purple Teaming & Agentic Threat Remediation.</p>
                <button onclick="startDashboard()" class="px-8 py-4 bg-purple-600 hover:bg-purple-500 transition text-white rounded font-bold shadow-[0_0_15px_rgba(168,85,247,0.5)] text-lg w-full">Initialize Swarm Simulation</button>
            </div>
        </div>

        <header class="flex-none flex flex-col gap-4 lg:flex-row lg:justify-between lg:items-center mb-4 sm:mb-5 border-b border-slate-800 pb-4 min-w-0">
            <div>
                <h1 class="text-2xl sm:text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 tracking-tight">A2Z SOC : AEGIS SWARM</h1>
                <p class="text-slate-400 text-sm mt-1 max-w-2xl">Autonomous Lead Generation & Purple Team Bootstrapping</p>
            </div>
            <div class="flex items-center gap-3 bg-slate-900 px-4 py-2 rounded-full border border-slate-800">
                <span class="relative flex h-3 w-3"><span id="status-ping" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span id="status-dot" class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span></span>
                <span id="status-text" class="text-emerald-400 font-bold uppercase tracking-wider text-sm">System Nominal</span>
            </div>
        </header>

        <div class="dashboard-shell dashboard-grid grid grid-cols-1 xl:grid-cols-4 gap-4 lg:gap-6 flex-1 min-h-0 overflow-hidden">
            <div class="flex flex-col gap-4 col-span-1 min-h-0 overflow-hidden">
                <div id="red-card" class="card p-4"><h2 class="text-lg font-bold text-red-400 mb-2 flex items-center gap-2"><span class="h-6 w-6 rounded bg-red-500/20 flex items-center justify-center">R</span> Red Hive</h2><div class="bg-slate-950 p-2 rounded text-xs font-mono text-slate-500" id="red-status">DORMANT</div></div>
                <div id="blue-card" class="card glow-blue p-4"><h2 class="text-lg font-bold text-blue-400 mb-2 flex items-center gap-2"><span class="h-6 w-6 rounded bg-blue-500/20 flex items-center justify-center">B</span> Blue Hive (IDS)</h2><div class="bg-slate-950 p-2 rounded text-xs font-mono text-blue-400" id="blue-status">MONITORING</div></div>
                <div id="commander-card" class="card p-4"><h2 class="text-lg font-bold text-purple-400 mb-2 flex items-center gap-2"><span class="h-6 w-6 rounded bg-purple-500/20 flex items-center justify-center">P</span> Purple Commander</h2><div class="bg-slate-950 p-2 rounded text-xs font-mono text-slate-500" id="commander-status">STANDBY</div></div>
            </div>

            <div class="card col-span-1 xl:col-span-2 flex flex-col min-h-0 overflow-hidden">
                <div class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-3 mb-4">
                    <div class="sensor"><div class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">CPU Load</div><div id="cpu-text" class="text-xl font-bold text-emerald-400">15.0%</div></div>
                    <div class="sensor"><div class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Snort IDS</div><div id="snort-text" class="text-xl font-bold text-emerald-400">0</div></div>
                    <div class="sensor"><div class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">WAF Blocks</div><div id="waf-text" class="text-xl font-bold text-emerald-400">0</div></div>
                    <div class="sensor"><div class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Auth Fails</div><div id="auth-text" class="text-xl font-bold text-emerald-400">0</div></div>
                    <div class="sensor"><div class="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1">Disk I/O</div><div id="disk-text" class="text-xl font-bold text-emerald-400">5 MB/s</div></div>
                </div>
                <div class="flex-1 relative min-h-[180px] sm:min-h-[220px] mb-4 overflow-hidden"><canvas id="cpuChart"></canvas></div>
                <div class="text-xs text-slate-500 font-bold uppercase tracking-widest mb-2">Live Swarm Telemetry</div>
                <div class="bg-slate-950 rounded border border-slate-800 p-3 flex-1 min-h-[220px] lg:min-h-0 log-container flex flex-col gap-1 panel-scroll" id="terminal-logs"></div>
            </div>

            <div class="card col-span-1 flex flex-col min-h-0 overflow-hidden">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-lg font-bold text-slate-200">AI Executions</h2>
                    <span class="text-[10px] bg-purple-500/20 text-purple-400 px-2 py-1 rounded font-bold uppercase">Gemini 2.5 Pro MCP</span>
                </div>
                <div class="flex-1 min-h-[220px] lg:min-h-0 bg-slate-950 rounded border border-slate-800 p-3 log-container flex flex-col gap-2 panel-scroll" id="mcp-logs">
                    <div class="text-slate-600 text-center mt-10 italic">Awaiting threat detection...</div>
                </div>
            </div>
        </div>

        <script>
            let audioEnabled = false;
            let pitchPhase = 0;
            
            const pitch1 = "Security Operation Centers are overwhelmed. It takes 277 days to stop a breach. We built Aegis Swarm: an autonomous A I hive-mind that automates Purple Teaming for our enterprise platform, A 2 Z SOC dot com. Watch closely as the Red Hive initiates a Kill Chain attack, and the Purple Commander dynamically neutralizes it using Gemini 2.5 Pro.";
            const pitch2 = "The Purple Commander just executed an unparalleled 6-partner integration. It evaluated Dynatrace telemetry, synced baselines via Fivetran, stored I O Cs in MongoDB, pushed signatures to Elastic SIEM, created a Git Lab Incident with a generated MITRE Caldera profile, and logged its reasoning to Arize A I. This is how we bootstrap cybersecurity. Thank you.";

            function speakText(text) {
                let msg = new SpeechSynthesisUtterance(text);
                let v = window.speechSynthesis.getVoices().find(v => v.name.includes('Samantha') || v.name.includes('Google US English'));
                if(v) msg.voice = v;
                window.speechSynthesis.speak(msg);
            }

            function showToast(message) {
                const container = document.getElementById('toast-container');
                const toast = document.createElement('div');
                toast.className = 'w-full bg-slate-900 border border-orange-500/50 shadow-[0_0_15px_rgba(249,115,22,0.3)] text-white px-5 py-4 rounded-lg flex items-center gap-4 transform transition-all duration-500 translate-x-10 opacity-0 mb-3';
                toast.innerHTML = `<span class="text-3xl">🦊</span><div><p class="font-bold text-sm text-orange-400">GITLAB INCIDENT</p><p class="text-sm text-slate-200 mt-1">${message}</p></div>`;
                container.appendChild(toast);
                requestAnimationFrame(() => toast.classList.remove('translate-x-10', 'opacity-0'));
                setTimeout(() => {
                    toast.classList.add('translate-x-10', 'opacity-0');
                    setTimeout(() => toast.remove(), 500);
                }, 6000);
            }

            function startDashboard() {
                document.getElementById('audio-overlay').style.display = 'none';
                audioEnabled = true; 
                let unlock = new SpeechSynthesisUtterance('');
                window.speechSynthesis.speak(unlock);
                speakText(pitch1);
                pitchPhase = 1;
                fetch('/start_simulation', {method: 'POST'});
            }

            const ctx = document.getElementById('cpuChart').getContext('2d');
            const cpuData = Array(30).fill(15);
            const chart = new Chart(ctx, {
                type: 'line', data: { labels: Array(30).fill(''), datasets: [{ data: cpuData, borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', borderWidth: 2, fill: true, pointRadius: 0 }] },
                options: { responsive: true, maintainAspectRatio: false, animation: { duration: 0 }, scales: { y: { min: 0, max: 100, grid: { color: '#1e293b'} }, x: { grid: { display: false } } }, plugins: { legend: { display: false } } }
            });

            const terminal = document.getElementById('terminal-logs');
            const mcpPanel = document.getElementById('mcp-logs');
            let lastLogId = 0;
            let lastMcpId = 0;

            setInterval(async () => {
                try {
                    const res = await fetch('/api/state'); const data = await res.json();
                    
                    cpuData.push(data.cpu_percent); cpuData.shift(); chart.update();
                    document.getElementById('cpu-text').innerText = data.cpu_percent.toFixed(1) + '%';
                    document.getElementById('snort-text').innerText = data.snort_alerts;
                    document.getElementById('waf-text').innerText = data.waf_blocks;
                    document.getElementById('auth-text').innerText = data.auth_failures;
                    document.getElementById('disk-text').innerText = data.disk_io_mbps + ' MB/s';

                    if (pitchPhase === 1 && data.under_attack) {
                        pitchPhase = 2; 
                    } else if (pitchPhase === 2 && !data.under_attack) {
                        pitchPhase = 3; 
                        setTimeout(() => { speakText(pitch2); }, 3000);
                    }

                    const isAttack = data.under_attack;
                    ['cpu', 'snort', 'waf', 'auth', 'disk'].forEach(id => {
                        document.getElementById(`${id}-text`).className = `text-xl font-bold ${data[id === 'cpu' ? 'cpu_percent' : id === 'disk' ? 'disk_io_mbps' : id + (id==='snort'?'_alerts':id==='waf'?'_blocks':'_failures')] > (id==='cpu'?20:id==='disk'?10:0) ? 'text-red-500 drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : 'text-emerald-400'}`;
                    });

                    if (isAttack) {
                        chart.data.datasets[0].borderColor = '#ef4444'; chart.data.datasets[0].backgroundColor = 'rgba(239, 68, 68, 0.15)';
                        document.getElementById('status-text').innerText = 'THREAT: ' + data.current_threat; document.getElementById('status-text').className = 'text-red-500 font-bold uppercase tracking-wider';
                        document.getElementById('status-ping').classList.replace('bg-emerald-400', 'bg-red-500'); document.getElementById('status-dot').classList.replace('bg-emerald-500', 'bg-red-600');
                        document.getElementById('red-card').classList.add('glow-red'); document.getElementById('red-status').innerText = 'EXECUTING'; document.getElementById('red-status').className = 'bg-slate-900 p-2 rounded text-xs font-mono text-red-400';
                        document.getElementById('commander-card').classList.add('glow-purple'); document.getElementById('commander-status').innerText = 'AI ACTIVE'; document.getElementById('commander-status').className = 'bg-slate-900 p-2 rounded text-xs font-mono text-purple-400';
                    } else {
                        chart.data.datasets[0].borderColor = '#10b981'; chart.data.datasets[0].backgroundColor = 'rgba(16, 185, 129, 0.1)';
                        document.getElementById('status-text').innerText = 'System Nominal'; document.getElementById('status-text').className = 'text-emerald-400 font-bold uppercase tracking-wider';
                        document.getElementById('status-ping').classList.replace('bg-red-500', 'bg-emerald-400'); document.getElementById('status-dot').classList.replace('bg-red-600', 'bg-emerald-500');
                        document.getElementById('red-card').classList.remove('glow-red'); document.getElementById('red-status').innerText = 'DORMANT'; document.getElementById('red-status').className = 'bg-slate-950 p-2 rounded text-xs font-mono text-slate-500';
                        document.getElementById('commander-card').classList.remove('glow-purple'); document.getElementById('commander-status').innerText = 'STANDBY'; document.getElementById('commander-status').className = 'bg-slate-950 p-2 rounded text-xs font-mono text-slate-500';
                    }

                    const newLogs = data.logs.filter(l => l.id > lastLogId);
                    if (newLogs.length > 0) {
                        newLogs.forEach(log => {
                            const div = document.createElement('div'); div.className = log.color;
                            div.innerHTML = `<span class="opacity-50">[${log.sender}]</span> > ${log.msg}`;
                            terminal.appendChild(div);
                            lastLogId = log.id;
                        });
                        requestAnimationFrame(() => { terminal.scrollTop = terminal.scrollHeight; });
                    }

                    const newMcpLogs = data.mcp_logs.filter(l => l.id > lastMcpId);
                    if (newMcpLogs.length > 0) {
                        if (lastMcpId === 0) mcpPanel.innerHTML = "";
                        newMcpLogs.forEach(log => {
                            const div = document.createElement('div'); 
                            div.className = "mcp-item text-purple-300";
                            div.innerHTML = `<span class="text-white font-bold block mb-1">${log.msg.replace('🚀 MCP TRIGGERED:', '⚡ Tool Executed:')}</span>`;
                            mcpPanel.appendChild(div);
                            lastMcpId = log.id;
                        });
                        requestAnimationFrame(() => { mcpPanel.scrollTop = mcpPanel.scrollHeight; });
                    }

                    if (data.toast_queue && data.toast_queue.length > 0) {
                        data.toast_queue.forEach(msg => showToast(msg));
                    }
                    if (audioEnabled && data.audio_queue && data.audio_queue.length > 0) {
                        data.audio_queue.forEach(msg => speakText(msg));
                    }
                } catch (e) {}
            }, 1000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
