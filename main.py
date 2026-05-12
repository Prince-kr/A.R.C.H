import argparse
from database.connection import init_db
from core.orchestrator import Orchestrator
from utils.logger import Logger
import json
import os

def main():
    parser = argparse.ArgumentParser(description="A.R.C.H.: Automated Reproducible Cyber Hardening CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    subparsers.add_parser("init", help="Initialize the database and environment")

    # Check command
    subparsers.add_parser("check", help="Verify system dependencies (Docker, Python)")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a sequential attack-defense cycle")
    run_parser.add_argument("--attack", default="dos_attack", help="Name of the red script to run")
    run_parser.add_argument("--target", required=True, help="Target IP address or Hostname (e.g., 192.168.100.2 or scanme.nmap.org)")
    run_parser.add_argument("--payload", default="", help="Optional payload for the attack")
    run_parser.add_argument("--defend", default="log_monitor", help="Name of the blue script to run")

    # Run Scenario command
    scenario_parser = subparsers.add_parser("run-scenario", help="Run a pre-defined scenario from scenarios.yaml")
    scenario_parser.add_argument("name", help="Name of the scenario to run")
    scenario_parser.add_argument("--target", required=True, help="Target IP address or Hostname")

    # Testbed commands
    tb_parser = subparsers.add_parser("testbed", help="Manage the Docker testbed")
    tb_parser.add_argument("action", choices=["up", "down"], help="Bring the testbed up or down")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export the database to a JSON file")
    export_parser.add_argument("--filename", default="data/exports/latest_export.json", help="Export destination")

    # Monitor command (Real-time Defense)
    monitor_parser = subparsers.add_parser("monitor", help="Run a Blue Team script in real-time monitoring mode")
    monitor_parser.add_argument("--defend", required=True, help="Name of the blue script to run")
    monitor_parser.add_argument("--interval", type=int, default=2, help="Seconds between checks")

    # Menu command (Interactive Mode)
    subparsers.add_parser("menu", help="Start the interactive A.R.C.H. menu")

    args = parser.parse_args()
    orchestrator = Orchestrator()

    if not args.command or args.command == "menu":
        from core.menu import InteractiveMenu
        menu = InteractiveMenu(orchestrator)
        menu.main_menu()
    elif args.command == "init":
        init_db()
        Logger.success("Database initialized.")
    elif args.command == "run":
        orchestrator.run_sequential_cycle(args.attack, args.target, args.payload, args.defend)
    if args.command == "testbed":
        # Check if docker-compose or docker compose is available
        compose_cmd = "docker-compose"
        if os.system("docker-compose --version > NUL 2>&1") != 0:
            if os.system("docker compose version > NUL 2>&1") == 0:
                compose_cmd = "docker compose"
            else:
                Logger.error("Neither 'docker-compose' nor 'docker compose' found. Please install Docker Compose.")
                return

        if args.action == "up":
            Logger.info(f"Starting Docker testbed using {compose_cmd}...")
            res = os.system(f"{compose_cmd} up -d --build")
            if res == 0:
                Logger.success("Testbed is running.")
            else:
                Logger.error("Failed to start testbed.")
        elif args.action == "down":
            Logger.info(f"Stopping Docker testbed using {compose_cmd}...")
            res = os.system(f"{compose_cmd} down")
            if res == 0:
                Logger.success("Testbed stopped.")
            else:
                Logger.error("Failed to stop testbed.")
    elif args.command == "check":
        Logger.info("Checking environment dependencies...")
        
        # Docker Check
        docker_check = os.system("docker --version > NUL 2>&1")
        if docker_check == 0:
            Logger.success("Docker found.")
            # Check for arch_net
            net_check = os.popen("docker network ls").read()
            if "arch_net" in net_check:
                Logger.success("Docker network 'arch_net' identified.")
            else:
                Logger.warning("Docker network 'arch_net' not found. Run 'testbed up' first.")
        else:
            Logger.warning("Docker NOT found. Testbed commands will fail.")
        
        # Tool Checks
        for tool in ["nmap", "hydra", "msfconsole"]:
            tool_check = os.system(f"{tool} --version > NUL 2>&1")
            if tool_check == 0:
                Logger.success(f"Tool '{tool}' is installed on host.")
            else:
                Logger.info(f"Tool '{tool}' not found on host (can still run via Docker).")

        if os.path.exists("data"):
            Logger.success("Data directory exists.")
        else:
            Logger.warning("Data directory missing. Run 'init' first.")

    elif args.command == "run-scenario":
        import yaml
        try:
            with open("scenarios.yaml", "r") as f:
                data = yaml.safe_load(f)
                scenario = next((s for s in data["scenarios"] if s["name"] == args.name), None)
                if scenario:
                    Logger.info(f"Running Scenario: [bold yellow]{scenario['name']}[/bold yellow]")
                    Logger.info(f"Description: {scenario.get('description', 'N/A')}")
                    orchestrator.run_sequential_cycle(
                        scenario["attack"], 
                        args.target, 
                        scenario.get("payload", ""), 
                        scenario["defend"]
                    )
                else:
                    Logger.error(f"Scenario '{args.name}' not found in scenarios.yaml")
        except Exception as e:
            Logger.error(f"Error loading scenarios: {str(e)}")

    elif args.command == "export":
        Logger.info(f"Generating full knowledge record for export...")
        os.makedirs(os.path.dirname(args.filename), exist_ok=True)
        
        data = orchestrator.repo.get_full_knowledge_record()
        
        with open(args.filename, "w") as f:
            json.dump(data, f, indent=2)
        
        Logger.success(f"Knowledge Record Exported to {args.filename}")
    elif args.command == "monitor":
        import time
        Logger.info(f"[*] Starting real-time monitoring with {args.defend}...")
        Logger.info("[*] Press Ctrl+C to stop.")
        try:
            while True:
                # We use a special session name for real-time monitoring
                orchestrator.defense_engine.run_script(args.defend, "realtime_monitor")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            Logger.info("\n[*] Monitoring stopped.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
