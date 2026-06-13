Markdown
# Python-Based Command & Control (C2) Framework Simulation

A modular, lightweight Command and Control (C2) infrastructure prototype written in native Python. This project serves as an educational simulation to demonstrate the underlying networking, beaconing, and egress communication mechanics utilized by professional Red Teams and advanced persistent threats (APTs). 

It was built specifically to study how malicious communication channels operate so that security analysts can better configure Endpoint Detection and Response (EDR) systems and network monitoring tools.

---

## 📐 Architecture & Communication Flow

This framework splits the control loop into two distinct operational components:

1. **The C2 Server (`c2_server.py`):** Acts as the attacker's listener infrastructure. It opens an HTTP socket, provisions an interactive terminal shell interface for the operator, queues commands, and processes incoming exfiltrated data.
2. **The C2 Beacon (`c2_beacon.py`):** Acts as the target endpoint implant. It uses a low-profile footprint with native system libraries to check in at a designated "heartbeat" interval, grab queued instructions, execute them via system sub-processes, and return the execution payload.

### The Network Loop:
* **Egress Polling (GET):** The beacon sends an HTTP GET request to the loopback interface (`127.0.0.1`) every 5 seconds checking for instructions.
* **Command Execution:** If a command is present, the beacon ingests the string and passes it securely to the operating system's background shell environment.
* **Data Exfiltration (POST):** The output of the command is bundled into an HTTP POST request and sent back to the server, where the listener console prints it for the operator.

---

## 🛠️ Technical Features & Hardening

* **Zero-Dependency Footprint:** Built entirely using native Python libraries (`http.server`, `socketserver`, and `urllib`). It relies on no third-party packages, mimicking real-world malware designed to bypass standard file-integrity or package-monitoring alarms.
* **Resilient Network Handling:** The beacon includes automated error handling via `urllib.error.URLError`. If the server goes offline or the connection drops, the beacon silently fails open and retries on the next heartbeat cycle without crashing.
* **Cross-Platform Stream Aggregation:** Uses `subprocess.Popen` with combined standard streams (`stdout + stderr`) to guarantee that both successful execution strings and system error messages are successfully captured and exfiltrated.

---

## 🚀 Local Lab Deployment & Testing

To safely run and evaluate this simulation in an isolated local testing environment, follow these steps:

1. Environment Setup
Clone this repository to your local directory:
```bash
git clone https://github.com/pallavikhadse/python-c2-framework-simulation.git
cd python-c2-framework-simulation

2. Launching the Operator Console
Open a terminal window and execute the listener server:
```bash
python c2_server.py
The terminal will initialize and enter a listening state: [*] C2 Server active on port 8080...

3. Activating the Target Beacon
Open a second, separate terminal window (or a split pane in VS Code) and run the beacon script:
```bash
python c2_beacon.py
The beacon will establish its heartbeat loop: [*] Target Beacon Started. Initiating callback loop..

4. Executing a Command Simulation
Return to your server terminal pane, which now displays the C2-Shell> prompt. Type a native system discovery command and press Enter:

Plaintext
C2-Shell> whoami
[*] Command 'whoami' queued. Waiting for next beacon check-in...

[+] Exfiltrated Output From Target:
----------------------------------------
desktop-example\user
----------------------------------------

🛑 Defensive Takeaways & EDR Insights
Developing this simulation highlights key focal points for defensive engineering and threat hunting:

Beaconing Detection: Security operations centers (SOCs) can detect this activity by looking for consistent HTTP polling intervals (e.g., traffic every 5 seconds) coming from a single endpoint to an external address.

User-Agent Anomalies: Standard Python scripts send a default HTTP User-Agent string (e.g., Python-urllib/3.x). EDR and proxy rules should be written to alert on non-browser User-Agents making outbound web requests.

⚖️ Disclaimer
This software is provided strictly for educational, security research, and authorized defensive benchmarking purposes. It should only be deployed in controlled, local virtual environments or authorized sandbox networks.