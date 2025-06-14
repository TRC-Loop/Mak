# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "orjson",
#     "platformdirs",
#     "rich",
# ]
# ///

import sys
import pathlib
import os
import orjson
from platformdirs import user_config_dir
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Group

console = Console()

VERSION = (1, 0, 0)

APP_NAME = "TRC-Loop/Mak"
CONFIG_NAME = "settings.json"

_config_dir = user_config_dir(APP_NAME)
_config_path = os.path.join(_config_dir, CONFIG_NAME)

def load_config():
    if not os.path.exists(_config_path):
        return {}
    with open(_config_path, 'r') as f:
        return orjson.loads(f.read())

def save_config(cfg: dict):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_path, 'wb') as f:
        f.write(orjson.dumps(cfg, option=orjson.OPT_INDENT_2))

def handle_makro(makro: str, args: list) -> None:
    print(makro, args)


def display_help(error: str = ""):
    error_text = Text()
    if error:
        error_text.append("ERROR: ", style="bold red")
        error_text.append(error, style="red")

    version_str = ".".join(map(str, VERSION))

    help_text = Text()
    if error_text:
        console.print(error_text)

    help_text.append("Mak - Aliases, Macros and advanced command-chains.\n", style="bold cyan")
    help_text.append("Github: ")
    help_text.append("https://github.com/TRC-Loop/Mak\n", style="grey37 underline")
    help_text.append(f"Version: {version_str}\n\n", style="bold")

    help_text.append("Usage:\n", style="bold")
    help_text.append("  mak <command>\n")
    help_text.append("  or: <shortcut> <macro> <args*>\n")
    help_text.append("  * optional\n\n")

    table = Table(show_header=False, pad_edge=False, title="Commands")
    table.add_column(justify="left", no_wrap=True)
    table.add_column(justify="left")

    commands = [
        ("help", "show this help"),
        ("version", "show version"),
        ("shortcuts list", "list all shortcuts"),
        ("shortcuts add <cmd>", "add a new shortcut"),
        ("shortcuts remove <cmd>", "remove a shortcut"),
        ("macros add <name> <shortcut> <commands>", "create a new macro"),
        ("macros remove <name>", "remove a macro"),
        ("macros list", "list all macros"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    # Group text and table together inside one Panel
    group = Group(help_text, table)

    console.print(Panel(group, border_style="cyan", title="Mak Help"))

def display_version():
    console.print("Version: " + ".".join(map(str, VERSION)))

if __name__ == "__main__":
    cfg = load_config()
    
    if not cfg:
        save_config(cfg)

    full_command = sys.argv
    executable = full_command[0]

    if len(full_command) < 2:
        display_help("Not enough commands")
        sys.exit(-1)

    command = full_command[1]

    match command:
        case "help":
            display_help()
        case "version":
            display_version()
    sys.exit(0)


