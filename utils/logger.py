from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "attack": "bold magenta",
    "defend": "bold blue"
})

console = Console(theme=custom_theme)

class Logger:
    @staticmethod
    def info(message: str):
        console.print(f"[info]INFO:[/info] {message}")

    @staticmethod
    def warning(message: str):
        console.print(f"[warning]WARNING:[/warning] {message}")

    @staticmethod
    def error(message: str):
        console.print(f"[error]ERROR:[/error] {message}")

    @staticmethod
    def success(message: str):
        console.print(f"[success]SUCCESS:[/success] {message}")

    @staticmethod
    def attack(message: str):
        console.print(f"[attack]ATTACK:[/attack] {message}")

    @staticmethod
    def defend(message: str):
        console.print(f"[defend]DEFEND:[/defend] {message}")
