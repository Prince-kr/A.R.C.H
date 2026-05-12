# A.R.C.H.: Automated Reproducible Cyber Hardening

A.R.C.H. is a professional-grade Cyber Experimentation Framework. It automates the execution of offensive security tools (Red Team) and synchronizes them with defensive telemetry collection (Blue Team). All actions are committed to an immutable "Knowledge Record" for AI training and security analysis.

---

## 🏗️ Architecture Overview

A.R.C.H. operates on a **Sequential Knowledge-Driven Pipeline**:
1. **Orchestration**: The `core` engine manages the timing and synchronization of tools.
2. **Execution**: The `Executor` utility handles subprocesses with isolation, timeouts, and command-injection protection.
3. **Persistence**: Every stdout, exit status, and telemetry finding is stored in a relational SQLite database via **SQLAlchemy**.
4. **Knowledge Record**: Use the `export` command to generate high-fidelity JSON datasets from your experiments.

---

## 🚀 Beginner's Setup Guide

This guide covers everything from zero to running your first experiment.

### Step 1: Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.10 or higher**: [Download from python.org](https://www.python.org/downloads/)
- **Docker & Docker Desktop**: [Download from docker.com](https://www.docker.com/products/docker-desktop/) (Required for the Testbed)

### Step 2: Extracting and Environment Setup
Open your terminal (Command Prompt/PowerShell on Windows, Terminal on Linux/Mac) and run the following:

#### **🪟 Windows**
```powershell
# Navigate to the project folder
cd ARCH_Working_Model

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install required libraries
pip install -r requirements.txt
```

#### **🐧 Linux / 🍎 macOS**
```bash
# Navigate to the project folder
cd ARCH_Working_Model

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required libraries
pip install -r requirements.txt
```

### Step 3: Database Initialization
Before running any tests, you must initialize the database:
```bash
python main.py init
```
This will create a `data/` folder and the `purple_team.db` file.

### Step 4: System Readiness Check
Run the built-in check tool to see if your machine has the necessary tools:
```bash
python main.py check
```

### Step 5: Running your first experiment
Once your environment is validated, you have two ways to interact with A.R.C.H.:

#### **Option A: Interactive Menu (Recommended)**
Simply run the main command without arguments to enter the guided menu:
```bash
python main.py
```
This interactive mode allows you to:
- Select **Attack Only**, **Defense Only**, or **Purple Team** modes.
- Run **Simultaneous Simulations** (Attack + Defense in parallel).
- Access a built-in **Help Hub** to understand tools and scenarios.
- Navigate easily with **Back** and **Exit** options.

#### **Option B: Command Line Interface (Power Users)**
Follow this sequence for direct CLI control:
1. **Start the Lab**: `python main.py testbed up` *(Note: This automatically builds the attacker and victim Dockerfiles. Initial build requires internet access. If it hangs on Windows/WSL, restart Docker Desktop).*
2. **Run a Scenario**: `python main.py run-scenario full_recon --target 192.168.100.2`
3. **Check the Database**: `python main.py export --filename data/exports/results.json`
4. **Tear down the Lab**: `python main.py testbed down`

---

## ⌨️ Advanced Usage: Understanding Payloads

The **"Payload"** field in the Interactive Menu (or `--payload` in CLI) allows you to pass raw arguments directly to the underlying security tools. This is equivalent to typing flags in a terminal.

**Pattern:** `[Tool Script] --target [Target] --payload "[Your Flags]"`

| Tool | Payload Example | Resulting Action |
| :--- | :--- | :--- |
| **nmap_scan** | `-sV -p 80,443` | Targeted service scan on Web ports. |
| **hydra_brute**| `ssh` | Focuses the attack on the SSH service. |
| **nikto_scan** | `-ssl -Tuning 4` | Scan with SSL and file enumeration focus. |
| **sqlmap_audit**| `--dbs --batch` | Automated database listing. |
| **msf_exploit** | `linux/x64/shell_reverse_tcp` | Specific Metasploit payload selection. |

---

## 🎮 Interactive Menu Modes

The A.R.C.H. Interactive Menu provides several ways to simulate security events:

1. **Red Team (Attack Only)**: Execute a standalone attack vector (e.g., Nmap Scan) without immediately running defense.
2. **Blue Team (Defense Only)**: Execute a defense script to check for historical alerts or start real-time monitoring.
3. **Purple Team (Sequential)**: The framework's core mode. Runs an attack followed immediately by a telemetry harvest for perfect data correlation.
4. **Simultaneous Run (Real-time Simulation)**: Launches the attack and starts the defense monitoring at the exact same time. This is useful for testing "Active Mitigation" efficacy where timing is critical.
5. **Scenarios Hub**: A library of pre-defined "Battle Plans" (like SQL Injection audits or Brute Force simulations).

---

## 🔬 Lab Setup (Suricata & Wazuh)

### 1. Suricata (Network Intrusion Detection)
A.R.C.H. expects Suricata to generate a `eve.json` file.
- **Windows/Linux/Mac (via Docker)**: Run `python main.py testbed up`. The Docker-compose file includes a pre-configured Suricata container.
- **Manual Setup**: 
    1. Install Suricata: `sudo apt install suricata`.
    2. Edit `/etc/suricata/suricata.yaml` and ensure the `outputs` section has `eve-log` enabled:
       ```yaml
       outputs:
         - eve-log:
             enabled: yes
             filetype: regular
             filename: eve.json
       ```
    3. Update rules: `sudo suricata-update`.
    4. Run: `sudo suricata -i eth0`.
    5. A.R.C.H. will read the logs from the path specified in `config.yaml`.

### 2. Wazuh (Endpoint Defense & SIEM)
Wazuh consists of a Manager and an Agent. The recommended approach for A.R.C.H. is to run the Manager via Docker and the Agent locally.

**Step 1: Start the Wazuh Manager (Using Docker)**
1. Clone the official repository and generate certs:
   ```bash
   git clone https://github.com/wazuh/wazuh-docker.git -b v4.7.3
   cd wazuh-docker/single-node
   docker-compose -f generate-indexer-certs.yml run --rm generator
   ```
2. Start the Manager:
   ```bash
   docker-compose up -d
   ```
   *(Wait 3-5 minutes. Dashboard available at `https://127.0.0.1` with default login: `admin`/`SecretPassword`)*

**Step 2: Install the Wazuh Agent on Kali/Ubuntu**
1. Add the repository key securely (modern method bypassing apt-key):
   ```bash
   curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --dearmor -o /usr/share/keyrings/wazuh-archive-keyring.gpg
   echo "deb [signed-by=/usr/share/keyrings/wazuh-archive-keyring.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee /etc/apt/sources.list.d/wazuh.list
   sudo apt-get update
   ```
2. Install the Agent:
   ```bash
   sudo apt-get install wazuh-agent -y
   ```

**Step 3: Authenticate and Start the Agent**
1. Link Agent to Manager (e.g., `127.0.0.1` if running locally):
   ```bash
   sudo /var/ossec/bin/agent-auth -m 127.0.0.1
   ```
2. Update the `<client><server><address>` to `127.0.0.1` in `/var/ossec/etc/ossec.conf`.
3. Enable and start the Agent:
   ```bash
   sudo systemctl enable wazuh-agent
   sudo systemctl start wazuh-agent
   ```

**Step 4: Connection Setup for A.R.C.H.**
Update `config.yaml` in A.R.C.H. to allow the Blue Team scripts to fetch alerts:
```yaml
wazuh:
  api_url: "https://127.0.0.1:55000"
  user: "admin"
  password: "SecretPassword"
```

---

## 🛠️ Running Experiments: Examples

### Example 1: Basic Nmap Scan vs Suricata Detection
This runs a Red Team Nmap scan and then uses a Blue Team script to check if Suricata detected it.
```bash
python main.py run --attack nmap_scan --target 192.168.100.2 --defend suricata_check
```

### Example 2: Brute Force Attempt vs Log Monitoring
This attempts to brute force SSH and then checks the host logs for failed login attempts.
```bash
python main.py run --attack hydra_brute --target 192.168.100.2 --defend log_monitor
```

### Example 3: Running a Full Scenario
Scenarios are pre-written "Battle Plans" in `scenarios.yaml`.
```bash
# Run the 'full_recon' scenario against the local lab victim
python main.py run-scenario full_recon --target 192.168.100.2

# Run a Metasploit exploit simulation
python main.py run-scenario exploit_simulation --target 192.168.100.2
```

---

## 🛡️ Real-Time Defense & Monitoring

While A.R.C.H. defaults to a "Sequential Cycle" for perfect data correlation, it also supports **Real-Time Monitoring** for live incident response simulation.

### Using the Monitor Command
To watch for alerts as they happen (e.g., in a separate terminal), use:
```bash
python main.py monitor --defend suricata_check --interval 5
```
This will loop the specified blue script every 5 seconds, allowing you to see detections live while you run attacks from another terminal.

---

---

## 🛠️ Tool & Scenario Registry

### 🔴 Red Team Tools (Offensive)
| Tool | Description | Targeted Vector |
|------|-------------|-----------------|
| `nmap_scan` | Network service detection | Port Scanning |
| `hydra_brute` | Login credential cracking | Authentication |
| `dos_attack` | Denial of Service simulation | Availability |
| `msf_exploit` | Metasploit payload execution | Exploitation |
| `nikto_scan` | Web server vulnerability scan | Web Security |
| `dirb_scan` | Directory/Content discovery | Information Leak |
| `sqlmap_audit` | SQL injection automation | Database |
| `gobuster_dns` | Subdomain enumeration | DNS |
| `slowloris_dos` | Layer 7 HTTP exhaustion | Application DoS |
| `smb_enumerate` | SMB/Samba share audit | Network Shares |

### 🔵 Blue Team Tools (Defensive)
| Tool | Description | Layer |
|------|-------------|-------|
| `suricata_check` | NIDS alert analysis | Network (L3/L4) |
| `log_monitor` | System log auditing | Host (L7) |
| `ip_blocker` | Active firewall mitigation | Network |
| `wazuh_alerts` | SIEM endpoint monitoring | Host/SIEM |
| `osquery_check` | System state analytics | Host |
| `clamav_scan` | Malware signature scan | File System |
| `rkhunter_check` | Rootkit detection | Kernel/Binaries |
| `fail2ban_status` | Brute-force block monitor | Service |
| `iptables_audit` | Firewall rule validation | Network |
| `docker_security` | Container hardening audit | Virtualization |

### 🎭 Pre-defined Research Scenarios
| Scenario Name | Red Tool | Blue Tool | Goal |
|---------------|----------|-----------|------|
| `full_recon` | `nmap_scan` | `suricata_check` | Network visibility audit |
| `credential_audit`| `hydra_brute`| `log_monitor` | Brute-force detection |
| `active_block` | `dos_attack` | `ip_blocker` | Automated mitigation |
| `web_vuln_scan` | `nikto_scan` | `suricata_check` | Web signature verification |
| `sql_injection_audit`| `sqlmap_audit`| `wazuh_alerts`| Database defense |
| `directory_bruteforce`| `dirb_scan` | `log_monitor` | Access log validation |
| `dns_exfiltration_test`| `gobuster_dns`| `suricata_check`| DNS anomaly detection |
| `layer7_dos_defense`| `slowloris_dos`| `fail2ban_status`| HTTP exhaustion defense |
| `smb_share_audit` | `smb_enumerate`| `osquery_check`| Unauthorized share detection |
| `container_hardening_test`| `msf_exploit`| `docker_security`| Escape detection |

---

## 📖 CLI Command Reference

| Command | Usage | Description |
|---------|-------|-------------|
| `(None)` | `python main.py` | Starts the **Interactive Menu** (Recommended). |
| `init` | `python main.py init` | Creates the database and folders. |
| `check` | `python main.py check` | Checks for Docker and Tool binaries. |
| `testbed up` | `python main.py testbed up` | Starts the Docker isolated network. |
| `testbed down`| `python main.py testbed down`| Stops the Docker isolated network. |
| `run` | `python main.py run --target ...`| Runs a single Red-Blue cycle. |
| `run-scenario`| `python main.py run-scenario <name> --target ...`| Runs a pre-defined flow. |
| `monitor` | `python main.py monitor --defend ...`| Runs a Blue script in a real-time loop. |
| `export` | `python main.py export --filename ...`| Saves all session data to JSON. |
| `menu` | `python main.py menu` | Explicitly enters interactive mode. |

---

## 📊 Research Reporting & Data Export

A.R.C.H. provides two methods to extract your data for academic or professional use:

### 1. Human-Readable Reports (Recommended for Thesis)
Generate structured Markdown reports for individual sessions:
1. Enter the **Interactive Menu** (`python main.py`).
2. Go to **Option 6: Results Viewer**.
3. Select your desired **Session ID**.
4. Choose **Option 4: Export to Markdown Report**.
*   **Output:** `data/exports/report_session_X.md` (Includes tools, status, and raw outputs).

### 2. Knowledge Record (JSON for Data Analysis)
Export the entire framework database for training AI or feeding into SIEMs:
- **Via Menu:** Results Viewer -> Select Session -> Option 2 (Raw JSON).
- **Via CLI:**
```bash
python main.py export --filename data/exports/full_dataset.json
```

---

## 🔬 Simulation vs. Production Use

The framework currently includes **Simulation Wrappers** for all 20+ tools in `scripts/red/` and `scripts/blue/`. These scripts allow you to test the orchestration logic, menu navigation, and database logging immediately without having the full security stack installed.

### Moving to Production:
To use real offensive tools, simply modify the Python scripts in `scripts/red/` to call the local binary. For example, in `nmap_scan.py`:
```python
# Change this:
print("[*] Simulating Nmap Scan...")
# To this:
import os
os.system(f"nmap {args.payload} {args.target}")
```

---

## 🎯 Safe Practice Targets & Guides

**⚠️ IMPORTANT WARNING:** It is strictly illegal to run offensive tools like Nmap, Hydra, Metasploit, or SQLmap against systems without explicit, written permission. Always use designated vulnerable environments.

Below is a guide on where to legally practice the offensive tools included in the A.R.C.H. framework, along with basic usage steps.

### 1. Nmap (Network Scanning)
*   **Legal Target:** `scanme.nmap.org` (Provided by the Nmap project explicitly for testing).
*   **How to run via A.R.C.H:** 
    ```bash
    python main.py run --attack nmap_scan --target scanme.nmap.org --payload "-sV"
    ```
*   **Manual Equivalent:** `nmap -sV scanme.nmap.org`

### 2. Hydra (Brute-Force)
*   **Legal Target:** You must set up a local vulnerable VM like **Metasploitable 2** or use platforms like **TryHackMe**. Do NOT brute-force public servers.
*   **How to run via A.R.C.H:**
    ```bash
    # Assuming your local Metasploitable VM is on 192.168.100.5
    python main.py run --attack hydra_brute --target 192.168.100.5 --payload "ssh"
    ```
*   **Manual Equivalent:** `hydra -l admin -P passwords.txt ssh://192.168.100.5`

### 3. Metasploit (Exploitation)
*   **Legal Target:** Local VMs like **Metasploitable 2/3** or HackTheBox instances.
*   **How to run via A.R.C.H:**
    ```bash
    python main.py run --attack msf_exploit --target 192.168.100.5 --payload "linux/x64/shell_reverse_tcp"
    ```
*   **Manual Equivalent:** Open `msfconsole`, type `use exploit/...`, set `RHOSTS`, and run `exploit`.

### 4. SQLmap, Nikto, and Dirb (Web Vulnerabilities)
*   **Legal Target:** `http://testphp.vulnweb.com/` (An intentionally vulnerable site hosted by Acunetix for testing web scanners).
*   **How to run via A.R.C.H:**
    ```bash
    python main.py run --attack sqlmap_audit --target "http://testphp.vulnweb.com/artists.php?artist=1" --payload "--dbs --batch"
    ```
    ```bash
    python main.py run --attack nikto_scan --target testphp.vulnweb.com
    ```

### 🏆 Recommended Free Cloud Labs for Practice
If you don't want to set up local Virtual Machines, create free accounts on these platforms. They provide legal, isolated target IPs (via VPN) to practice all A.R.C.H. tools safely:
1.  **[TryHackMe](https://tryhackme.com/):** Best for beginners. Provides guided rooms for Metasploit, Hydra, and Nmap.
2.  **[Hack The Box](https://www.hackthebox.com/):** Best for intermediate/advanced users looking to test real-world exploits.
3.  **[PortSwigger Web Security Academy](https://portswigger.net/web-security):** The gold standard for web vulnerabilities (SQLi, Dirb, Nikto practice).

---

## 🧪 Framework Testing
To verify the framework logic itself:
```bash
python -m pytest tests/
```

---

## 🔧 Troubleshooting

### 🐳 Docker "Named Pipe" Error (Windows)
If you see `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`:
1.  **Start Docker Desktop**: This error means the Docker service is not running.
2.  **Wait for Initialization**: Docker takes 1-2 minutes to start on Windows.

### 🛡️ Docker Permission Denied (Linux/WSL)
If you see `permission denied while trying to connect to the Docker daemon`, run: `sudo usermod -aG docker $USER`

### 🛠️ Tool Binary Not Found
If you see `[!] Error: 'tool' binary not found`:
1.  **Path Issue**: Install the tool (e.g., Nmap) and add its `bin` folder to your Windows System PATH.
2.  **Fallback**: The scripts now include an automatic **Simulation Fallback** so you can continue testing without the binaries.

---

## 🛡️ Security & Privacy
- **Isolation**: Always run experiments within the `testbed` (Docker) or a dedicated VM.
- **No Leaks**: The provided Docker network is configured with `internal: true` to prevent data leaking to the public internet.
- **Hardening**: Use the `Executor` class in `core/` to ensure all script calls are safe and timed out properly.
