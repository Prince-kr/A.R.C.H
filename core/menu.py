import os
import json
import yaml
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from utils.logger import Logger

class InteractiveMenu:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.console = Console()
        self.running = True

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self, title="MAIN MENU"):
        self.clear_screen()
        self.console.print(Panel(f"[bold cyan]A.R.C.H. Framework - {title}[/bold cyan]", expand=False))

    def main_menu(self):
        while self.running:
            self.display_header()
            self.console.print("1. [bold red]Red Team (Attack Only)[/bold red]")
            self.console.print("2. [bold blue]Blue Team (Defense Only)[/bold blue]")
            self.console.print("3. [bold magenta]Purple Team (Sequential Attack-Defense)[/bold magenta]")
            self.console.print("4. [bold green]Simultaneous Run (Real-time Simulation)[/bold green]")
            self.console.print("5. [bold yellow]Scenarios Hub[/bold yellow]")
            self.console.print("6. [bold cyan]Results Viewer (Database Explorer)[/bold cyan]")
            self.console.print("7. [bold white]Help & Documentation[/bold white]")
            self.console.print("8. [bold red]Exit[/bold red]")
            
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])

            if choice == "1":
                self.attack_menu()
            elif choice == "2":
                self.defense_menu()
            elif choice == "3":
                self.purple_menu()
            elif choice == "4":
                self.simultaneous_menu()
            elif choice == "5":
                self.scenario_menu()
            elif choice == "6":
                self.results_viewer()
            elif choice == "7":
                self.help_menu()
            elif choice == "8":
                self.running = False
                Logger.info("Exiting A.R.C.H. Goodbye!")

    def attack_menu(self):
        tools = self._load_metadata("red")
        while True:
            self.display_header("RED TEAM - ATTACK")
            table = Table(title="Available Attack Tools")
            table.add_column("ID", style="cyan")
            table.add_column("Tool Name", style="bold red")
            table.add_column("Description", style="white")
            
            tool_keys = list(tools.keys())
            for idx, tool in enumerate(tool_keys, 1):
                table.add_row(str(idx), tool, tools[tool]["description"])
            
            self.console.print(table)
            self.console.print("B. [yellow]Back to List[/yellow]")
            self.console.print("M. [bold cyan]Main Menu[/bold cyan]")
            
            choice = Prompt.ask("\nSelect a tool or 'B'/'M'", choices=[str(i) for i in range(1, len(tool_keys)+1)] + ["B", "b", "M", "m"])
            
            if choice.lower() == "b":
                return
            if choice.lower() == "m":
                self.main_menu()
                return
            
            tool_name = tool_keys[int(choice)-1]
            target = Prompt.ask("Enter target IP/Hostname", default="192.168.100.2")
            payload = Prompt.ask("Enter optional payload (press enter for default)", default="")
            
            self.console.print(f"\n[bold yellow]Preparing to Launch:[/bold yellow] {tool_name}")
            self.console.print(f"[bold yellow]Target:[/bold yellow] {target}")
            self.console.print(f"[bold yellow]Payload:[/bold yellow] {payload if payload else 'Default'}")
            
            Logger.info(f"Launching {tool_name} against {target}...")
            with self.console.status(f"[bold red]Executing {tool_name}...[/bold red]", spinner="bouncingBar"):
                session_id, stdout, status = self.orchestrator.run_standalone_attack(tool_name, target, payload)
            
            self.console.print(Panel(stdout, title=f"Raw Output - Session {session_id} - Status: {status}", border_style="red" if status != 0 else "green"))
            Prompt.ask("\nExecution finished. Press Enter to return to Tool List")

    def defense_menu(self):
        tools = self._load_metadata("blue")
        while True:
            self.display_header("BLUE TEAM - DEFENSE")
            table = Table(title="Available Defense Tools")
            table.add_column("ID", style="cyan")
            table.add_column("Tool Name", style="bold blue")
            table.add_column("Description", style="white")
            
            tool_keys = list(tools.keys())
            for idx, tool in enumerate(tool_keys, 1):
                table.add_row(str(idx), tool, tools[tool]["description"])
            
            self.console.print(table)
            self.console.print("B. [yellow]Back to List[/yellow]")
            self.console.print("M. [bold cyan]Main Menu[/bold cyan]")
            
            choice = Prompt.ask("\nSelect a tool or 'B'/'M'", choices=[str(i) for i in range(1, len(tool_keys)+1)] + ["B", "b", "M", "m"])
            
            if choice.lower() == "b":
                return
            if choice.lower() == "m":
                self.main_menu()
                return
            
            tool_name = tool_keys[int(choice)-1]
            mode = Prompt.ask("Select Mode", choices=["Check", "Monitor"], default="Check")
            
            if mode == "Check":
                session_id = Prompt.ask("Enter Session ID to check (or 'latest')", default="latest")
                with self.console.status(f"[bold blue]Extracting Telemetry...[/bold blue]"):
                    session_id, findings, status = self.orchestrator.run_standalone_defense(tool_name, session_id)
                self.console.print(Panel(findings, title=f"Defense Findings - Session {session_id} - Status: {status}", border_style="blue"))
            else:
                interval = IntPrompt.ask("Enter monitoring interval (seconds)", default=2)
                Logger.info(f"Starting real-time monitoring with {tool_name}. Press Ctrl+C to stop.")
                try:
                    while True:
                        self.orchestrator.defense_engine.run_script(tool_name, "realtime_monitor")
                        time.sleep(interval)
                except KeyboardInterrupt:
                    Logger.info("\nMonitoring stopped.")
            
            Prompt.ask("\nExecution finished. Press Enter to return to Tool List")

    def purple_menu(self):
        self.display_header("PURPLE TEAM - SEQUENTIAL")
        red_tools = list(self._load_metadata("red").keys())
        blue_tools = list(self._load_metadata("blue").keys())
        
        target = Prompt.ask("Enter target IP/Hostname", default="192.168.100.2")
        
        # Select Red
        self.console.print("\n[bold red]Select Attack Tool:[/bold red]")
        for idx, t in enumerate(red_tools, 1): self.console.print(f"{idx}. {t}")
        self.console.print("B. [yellow]Back[/yellow]")
        self.console.print("M. [bold cyan]Main Menu[/bold cyan]")
        
        r_choice = Prompt.ask("Choice", choices=[str(i) for i in range(1, len(red_tools)+1)] + ["B", "b", "M", "m"])
        if r_choice.lower() == "b": return
        if r_choice.lower() == "m": self.main_menu(); return
        red_tool = red_tools[int(r_choice)-1]
        
        # Select Blue
        self.console.print("\n[bold blue]Select Defense Tool:[/bold blue]")
        for idx, t in enumerate(blue_tools, 1): self.console.print(f"{idx}. {t}")
        self.console.print("B. [yellow]Back[/yellow]")
        self.console.print("M. [bold cyan]Main Menu[/bold cyan]")
        
        b_choice = Prompt.ask("Choice", choices=[str(i) for i in range(1, len(blue_tools)+1)] + ["B", "b", "M", "m"])
        if b_choice.lower() == "b": return
        if b_choice.lower() == "m": self.main_menu(); return
        blue_tool = blue_tools[int(b_choice)-1]
        
        payload = Prompt.ask("Enter optional payload", default="")
        
        Logger.info(f"Running Purple Cycle: {red_tool} -> {blue_tool} on {target}")
        with self.console.status(f"[bold magenta]Running Sequential Cycle...[/bold magenta]", spinner="earth"):
            session_id = self.orchestrator.run_sequential_cycle(red_tool, target, payload, blue_tool)
        
        self.console.print(Panel(f"Cycle completed successfully for Session [bold cyan]{session_id}[/bold cyan].\nAll telemetry has been committed to the Knowledge Record.", title="Purple Team Status", border_style="magenta"))
        
        show_now = Prompt.ask("\nView deep results now?", choices=["y", "n"], default="y")
        if show_now.lower() == "y":
            self.display_session_results(session_id)
        else:
            Prompt.ask("\nPress Enter to return")

    def simultaneous_menu(self):
        self.display_header("SIMULTANEOUS RUN")
        self.console.print("[yellow]Note: This will launch the attack and start defense monitoring simultaneously.[/yellow]")
        
        red_tools = list(self._load_metadata("red").keys())
        blue_tools = list(self._load_metadata("blue").keys())
        
        target = Prompt.ask("Enter target IP/Hostname", default="192.168.100.2")
        
        self.console.print("\n[bold red]Select Attack Tool:[/bold red]")
        for idx, t in enumerate(red_tools, 1): self.console.print(f"{idx}. {t}")
        r_choice = IntPrompt.ask("Choice", choices=[str(i) for i in range(1, len(red_tools)+1)])
        red_tool = red_tools[r_choice-1]
        
        self.console.print("\n[bold blue]Select Monitoring Tool:[/bold blue]")
        for idx, t in enumerate(blue_tools, 1): self.console.print(f"{idx}. {t}")
        self.console.print("B. [yellow]Back[/yellow]")
        self.console.print("M. [bold cyan]Main Menu[/bold cyan]")
        
        b_choice = Prompt.ask("Choice", choices=[str(i) for i in range(1, len(blue_tools)+1)] + ["B", "b", "M", "m"])
        if b_choice.lower() == "b": return
        if b_choice.lower() == "m": self.main_menu(); return
        blue_tool = blue_tools[int(b_choice)-1]
        
        payload = Prompt.ask("Enter optional payload", default="")

        import threading
        # Create a unified session for the simultaneous run
        testbed = self.orchestrator.repo.get_latest_testbed() or self.orchestrator.repo.create_testbed("Sim Lab", "192.168.100.0/24")
        session = self.orchestrator.repo.create_session(testbed.id, mode="simultaneous")
        
        def run_defense():
            Logger.info(f"Defense monitoring started ({blue_tool})...")
            findings, status = self.orchestrator.defense_engine.run_script(blue_tool, session.id)
            self.orchestrator.repo.log_defense(session.id, None, blue_tool, findings)

        def run_attack():
            Logger.info(f"Attack started ({red_tool})...")
            stdout, status = self.orchestrator.attack_engine.run_script(red_tool, target, payload)
            self.orchestrator.repo.log_attack(session.id, red_tool, target, payload, stdout, status)

        t1 = threading.Thread(target=run_defense)
        t2 = threading.Thread(target=run_attack)
        
        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
        
        Logger.success("Simultaneous execution completed.")
        Prompt.ask("\nPress Enter to return")

    def scenario_menu(self):
        scenarios = self._load_scenarios()
        while True:
            self.display_header("SCENARIOS HUB")
            table = Table(title="Cyber Battle Scenarios")
            table.add_column("ID", style="cyan")
            table.add_column("Scenario", style="bold yellow")
            table.add_column("Red", style="red")
            table.add_column("Blue", style="blue")
            table.add_column("Description", style="white")
            
            for idx, s in enumerate(scenarios, 1):
                table.add_row(str(idx), s["name"], s["attack"], s["defend"], s["description"])
            
            self.console.print(table)
            self.console.print("B. [yellow]Back to List[/yellow]")
            self.console.print("M. [bold cyan]Main Menu[/bold cyan]")
            
            choice = Prompt.ask("\nSelect a scenario or 'B'/'M'", choices=[str(i) for i in range(1, len(scenarios)+1)] + ["B", "b", "M", "m"])
            
            if choice.lower() == "b":
                return
            if choice.lower() == "m":
                self.main_menu()
                return
            
            scenario = scenarios[int(choice)-1]
            target = Prompt.ask("Enter target IP/Hostname", default="192.168.100.2")
            
            Logger.info(f"Running Scenario: {scenario['name']}")
            with self.console.status(f"[bold yellow]Executing Scenario: {scenario['name']}...[/bold yellow]", spinner="dots"):
                session_id = self.orchestrator.run_sequential_cycle(scenario["attack"], target, scenario.get("payload", ""), scenario["defend"])
            
            show_now = Prompt.ask("View results now?", choices=["y", "n"], default="y")
            if show_now.lower() == "y":
                self.display_session_results(session_id)
            else:
                Prompt.ask("\nPress Enter to return")

    def results_viewer(self):
        while True:
            self.display_header("RESULTS VIEWER")
            sessions = self.orchestrator.repo.get_all_sessions()
            if not sessions:
                self.console.print("[yellow]No sessions found in database.[/yellow]")
                Prompt.ask("\nPress Enter to return")
                return

            table = Table(title="Historical Sessions")
            table.add_column("ID", style="cyan")
            table.add_column("Timestamp", style="white")
            table.add_column("Testbed", style="green")
            
            for s in sessions[-20:]: # Show last 20 for better visibility
                table.add_row(str(s.id), str(s.start_time), str(s.testbed_id))
            
            self.console.print(table)
            self.console.print("L. [bold cyan]List All Session IDs[/bold cyan]")
            self.console.print("E. [bold magenta]Bulk Export All Sessions (PDF/TXT)[/bold magenta]")
            self.console.print("B. [yellow]Back to Main Menu[/yellow]")
            
            choice = Prompt.ask("\nEnter Session ID, 'L' to List All, 'E' to Export, or 'B'", default="B")
            
            if choice.lower() == "b":
                return
            if choice.lower() == "e":
                self.bulk_export_menu()
                continue
            if choice.lower() == "l":
                self._list_all_session_ids(sessions)
                continue
            
            try:
                session_id = int(choice)
                self.display_session_results(session_id)
            except ValueError:
                Logger.error("Invalid input. Enter a Session ID, 'L', 'E', or 'B'.")

    def _list_all_session_ids(self, sessions):
        self.display_header("ALL HISTORICAL SESSIONS")
        table = Table(title="Full Session History")
        table.add_column("ID", style="cyan")
        table.add_column("Timestamp", style="white")
        table.add_column("Mode", style="yellow")
        
        for s in sessions:
            table.add_row(str(s.id), str(s.start_time), s.mode)
        
        self.console.print(table)
        Prompt.ask("\nPress Enter to return")

    def bulk_export_menu(self):
        from utils.exporter import ReportExporter
        exporter = ReportExporter(self.orchestrator.repo)
        
        self.display_header("BULK EXPORT TOOL")
        self.console.print("Choose export format:")
        self.console.print("1. [bold white]Plain Text (.txt)[/bold white]")
        self.console.print("2. [bold red]Professional PDF (.pdf)[/bold red]")
        self.console.print("B. [yellow]Back[/yellow]")
        
        fmt = Prompt.ask("\nSelect format", choices=["1", "2", "B", "b"])
        if fmt.lower() == "b": return

        with self.console.status("[bold magenta]Generating Consolidated Report...[/bold magenta]"):
            if fmt == "1":
                path, msg = exporter.export_all_to_txt()
            else:
                path, msg = exporter.export_all_to_pdf()
        
        if path:
            self.console.print(Panel(f"Consolidated Narrative Report exported successfully!\nLocation: [bold green]{path}[/bold green]", border_style="green"))
        else:
            Logger.error(f"Export failed: {msg}")
        
        Prompt.ask("\nPress Enter to return")

    def display_session_results(self, session_id):
        data = self.orchestrator.repo.get_session_details(session_id)
        if not data:
            Logger.error(f"Session {session_id} not found in database.")
            time.sleep(1)
            return        
            
        while True:
            self.clear_screen()
            self.display_header(f"RESULTS - SESSION {session_id} ({data['mode']})")

            self.console.print("Select View Format:")
            self.console.print("1. [bold green]Summary Table[/bold green] (Human Readable)")
            self.console.print("2. [bold yellow]Raw JSON[/bold yellow] (Data Analysis)")
            self.console.print("3. [bold magenta]Narrative Report[/bold magenta] (Detailed Findings)")
            self.console.print("4. [bold cyan]Export to Markdown Report[/bold cyan]")
            self.console.print("B. [yellow]Back to List[/yellow]")
            
            fmt = Prompt.ask("\nChoice", choices=["1", "2", "3", "4", "B", "b"])
            
            if fmt.lower() == "b":
                return
            
            self.clear_screen()
            if fmt == "1":
                self._show_table_view(data)
            elif fmt == "2":
                self._show_json_view(data)
            elif fmt == "3":
                self._show_narrative_view(data)
            elif fmt == "4":
                self._export_report(data)
            
            Prompt.ask("\nPress Enter to return to View Options")

    def _export_report(self, data):
        filename = f"data/exports/report_session_{data['id']}.md"
        os.makedirs("data/exports", exist_ok=True)
        
        report = f"""# A.R.C.H. Framework - Session {data['id']} Report
**Timestamp:** {data['timestamp']}
**Mode:** {data['mode']}

## 🔴 Red Team Activity
- **Tool:** {data['attack']['tool']}
- **Target:** {data['attack']['target']}
- **Exit Status:** {data['attack']['status']}

### Raw Output Snippet:
```text
{data['attack']['stdout'][:1000]}
```

## 🔵 Blue Team Activity
- **Tool:** {data['defense']['tool']}
- **Findings Count:** {len(data['defense']['findings'])}

### Findings Details:
{json.dumps(data['defense']['findings'], indent=2)}

---
*Generated by A.R.C.H. Framework - Automated Reproducible Cyber Hardening*
"""
        with open(filename, "w") as f:
            f.write(report)
        
        self.console.print(Panel(f"Report exported to [bold green]{filename}[/bold green]", border_style="cyan"))

    def _show_table_view(self, data):
        table = Table(title=f"Session {data['id']} Summary")
        table.add_column("Component", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Attack Tool", data['attack']['tool'])
        table.add_row("Target", data['attack']['target'])
        table.add_row("Exit Status", str(data['attack']['status']))
        table.add_row("Defense Tool", data['defense']['tool'])
        table.add_row("Findings Count", str(len(data['defense']['findings'])))
        
        self.console.print(table)

    def _show_json_view(self, data):
        from rich.syntax import Syntax
        json_str = json.dumps(data, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title="Raw Knowledge Record"))

    def _show_narrative_view(self, data):
        report = f"""
        [bold underline]EXECUTIVE SUMMARY[/bold underline]
        On {data['timestamp']}, a cybersecurity experiment was conducted using the A.R.C.H. framework.
        
        [bold red]RED TEAM ACTIVITY:[/bold red]
        The system executed a [bold]{data['attack']['tool']}[/bold] against target [bold]{data['attack']['target']}[/bold].
        The attack returned an exit status of [bold]{data['attack']['status']}[/bold].
        Raw Output Snippet: {data['attack']['stdout'][:200]}...
        
        [bold blue]BLUE TEAM ACTIVITY:[/bold blue]
        Following the attack, the [bold]{data['defense']['tool']}[/bold] module was triggered for telemetry extraction.
        
        [bold green]FINDINGS & CORRELATION:[/bold green]
        The defense engine identified [bold]{len(data['defense']['findings'])}[/bold] specific security events related to this session.
        Correlation Integrity: [bold]High[/bold] (Sequential Synchronization enforced).
        
        [bold yellow]DATABASE STORAGE:[/bold yellow]
        All metadata has been committed to the persistent SQLite storage with Session ID {data['id']}.
        """
        self.console.print(Panel(report, title="Formal Research Narrative"))

    def help_menu(self):
        while True:
            self.display_header("HELP & DOCUMENTATION")
            self.console.print("1. Understand [bold red]Attack Tools[/bold red]")
            self.console.print("2. Understand [bold blue]Defense Tools[/bold blue]")
            self.console.print("3. Understand [bold yellow]Scenarios[/bold yellow]")
            self.console.print("4. [bold cyan]Framework Commands Guide[/bold cyan]")
            self.console.print("B. [yellow]Back to Main Menu[/yellow]")
            
            choice = Prompt.ask("\nSelect an option", choices=["1", "2", "3", "4", "B", "b"])
            
            if choice.lower() == "b":
                return
            
            if choice == "1":
                self._display_tool_help("red")
            elif choice == "2":
                self._display_tool_help("blue")
            elif choice == "3":
                self._display_scenario_help()
            elif choice == "4":
                self._display_general_help()
            
            Prompt.ask("\nPress Enter to return to Help Menu")

    def _display_tool_help(self, team):
        tools = self._load_metadata(team)
        self.display_header(f"HELP - {team.upper()} TOOLS")
        for name, meta in tools.items():
            self.console.print(Panel(f"[bold]{name}[/bold]\n{meta['description']}\n[cyan]Args:[/cyan] {meta.get('required_args', [])}", border_style="red" if team=="red" else "blue"))

    def _display_scenario_help(self):
        scenarios = self._load_scenarios()
        self.display_header("HELP - SCENARIOS")
        for s in scenarios:
            self.console.print(Panel(f"[bold]{s['name']}[/bold]\n{s['description']}\n[red]Attack:[/red] {s['attack']}\n[blue]Defense:[/blue] {s['defend']}", border_style="yellow"))

    def _display_general_help(self):
        self.display_header("COMMANDS GUIDE")
        guide = """
        [bold]Interactive Menu:[/bold] Run 'python main.py' without arguments.
        
        [bold]CLI Mode:[/bold]
        - [cyan]init[/cyan]: Setup database and folders.
        - [cyan]testbed up/down[/cyan]: Start/Stop Docker environment.
        - [cyan]run --attack X --target Y --defend Z[/cyan]: Run a Purple Team cycle.
        - [cyan]run-scenario NAME --target Y[/cyan]: Run a predefined scenario.
        - [cyan]monitor --defend X[/cyan]: Start continuous Blue Team monitoring.
        - [cyan]export[/cyan]: Save all results to a JSON file.
        
        [bold]Workflow:[/bold]
        1. Start Lab: 'testbed up'
        2. Execute Attack/Defense: Use Menu or CLI
        3. View Results: SQLite or Export
        """
        self.console.print(Panel(guide))

    def _load_metadata(self, team):
        path = f"scripts/{team}/metadata.json"
        with open(path, "r") as f:
            return json.load(f)

    def _load_scenarios(self):
        with open("scenarios.yaml", "r") as f:
            return yaml.safe_load(f)["scenarios"]
