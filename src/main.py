import typer
import subprocess
import os
import questionary
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align
from typing_extensions import Annotated, Optional
from typing import List
from platformdirs import user_config_dir
import orjson
import re

def sanitize_name(name: str) -> str:
    # Replace spaces and underscores with hyphens
    name = re.sub(r'[ _]+', '-', name)
    # Remove all non-valid characters (keep alphanum, hyphen)
    name = re.sub(r'[^a-zA-Z0-9\-]', '', name)
    # Lowercase
    return name.lower()


VERSION = (0,0,0)

DEV_DEBUG_MODE = os.getenv("MAK_DEBUG_MODE", False)
APP_NAME = os.getenv("MAK_APP_NAME", "TRCLoop/Mak")
CONFIG_NAME = os.getenv("MAK_CONFIG_NAME", "config.json")
DATASTORE_NAME = os.getenv("MAK_DATASTORE_NAME", "data.json")


GITHUB_LINK = "https://github.com/TRC-Loop/Mak"
ASCII_ART = "                                                               █████             \n                                                              ███████            \n     ██████████████████         ███████                       ███████            \n    ██████     █████████       ████████                       ███████            \n   ██████      █████████      ████████                       ███████             \n   ██████      █████████     █████████     ████████████████  █████████████████   \n   ██████     ███████████   ███ ██████   ██████    ███████   ████████  ███████   \n    ██████    ███████████  ███ ███████  ██████     ███████  ████████   ███████   \n             ████ ███████ ████ ███████ ███████    ████████  ███████    ███████   \n            █████  ██████████  ██████  ██████     ███████   ███████  ███████     \n            ████   █████████  ███████ ███████     ███████  ███████ ███████       \n           ████    ████████   ███████ ███████    ███████   ███████ ███████       \n         ██████     ██████    ███████ ███████    ███████  ████████  ███████      \n      ████████      █████     ███████  ██████   █████████ ███████   █████████    \n       █████        ████      ████████   ███████  ███████ ███████     ██████     \n                              ████████                                           \n                               ████████                                          \n                                 ████"
_config_dir = user_config_dir(APP_NAME)
_config_path = os.path.join(_config_dir, CONFIG_NAME)
_datastore_path = os.path.join(_config_dir, DATASTORE_NAME)

def load_config():
    if not os.path.exists(_config_path):
        return {}
    with open(_config_path, 'r') as f:
        return orjson.loads(f.read())

def load_data():
    if not os.path.exists(_datastore_path):
        return {}
    with open(_datastore_path, 'r') as f:
        return orjson.loads(f.read())

def save_config(cfg: dict):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_path, 'wb') as f:
        f.write(orjson.dumps(cfg, option=orjson.OPT_INDENT_2))

def save_data(data: dict):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_datastore_path, 'wb') as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

app = typer.Typer()

keybinds_app = typer.Typer()
macros_app = typer.Typer()
config_app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        info()

@app.command(name="version", help="Get Version Info")
def version(
    pure: Annotated[bool, typer.Option("--pure", "-p", "--raw", "-r", help="Return version only")] = False,
    sparse: Annotated[bool, typer.Option("--sparse", "-s", help="Show semantic version parts")] = False,
):
    base_ver = ".".join(map(str, VERSION))
    if pure:
        print(base_ver)
        raise typer.Exit()

    if sparse:
        print("Major:", VERSION[0])
        print("Minior:", VERSION[1])
        print("Patch:", VERSION[2])
        raise typer.Exit()

    print("Version:", base_ver)

@app.command(name="info", help="Display Info about Mak")
def info():
    print(ASCII_ART)
    print("Version",".".join(map(str, VERSION)))
    print("Github", GITHUB_LINK)
    print("Config Path", _config_path)
    print("Datastore Path", _datastore_path)
    print("App Name", APP_NAME)
    print("Debug Mode", DEV_DEBUG_MODE)
    print("For help, use --help")



@keybinds_app.command(name="add", help="Add a new Keybind")
def keybinds_add(keybind: Annotated[str, typer.Argument(help="Keybind name")]):
    data = load_data()
    _keybind = sanitize_name(keybind)

    if not _keybind == keybind:
        print(f"Sanitized: {keybind} → {_keybind}")

    if _keybind in data:
        print("Keybind already exists.")
        raise typer.Abort()

    data[_keybind] = {"macros": []}
    save_data(data)
    print(f"Added keybind: {_keybind}")


@keybinds_app.command(name="list", help="List all Keybinds")
def keybinds_list():
    data = load_data()
    keybinds = list(data.keys())

    if not keybinds:
        print("No keybinds found.")
        return

    console = Console()
    table = Table(title="Registered Keybinds")
    table.add_column("Index", justify="right", style="cyan")
    table.add_column("Keybind", style="magenta")

    for i, kb in enumerate(keybinds, 1):
        table.add_row(str(i), kb)

    print(table)


@keybinds_app.command(name="remove", help="Remove a Keybind")
def keybinds_remove(keybind: Annotated[str, typer.Argument(help="Keybind to remove")]):
    data = load_data()
    if keybind not in data:
        print("Keybind not found.")
        raise typer.Abort()

    del data[keybind]
    save_data(data)
    print(f"Removed keybind: {keybind}")



@macros_app.command(name="add", help="Create a new macro")
def macros_add(
    keybind: Annotated[str, typer.Argument(help="Existing keybind")],
    name: Annotated[str, typer.Argument(help="Name of the macro")],
    command: Annotated[str, typer.Argument(help="Command to run")],
    seperator: Annotated[str, typer.Option("--sep", "-s", help="Command separator")] = ";"
):
    data = load_data()

    if keybind not in data:
        print(f"Keybind '{keybind}' does not exist.")
        raise typer.Abort()

    macro = {
        "name": sanitize_name(name),
        "commands": command.split(seperator)
    }

    existing_macros = data[keybind].setdefault("macros", [])

    if any(m["name"] == macro["name"] for m in existing_macros):
        print(f"Macro '{macro['name']}' already exists under keybind '{keybind}'.")
        raise typer.Abort()

    existing_macros.append(macro)
    save_data(data)
    print(f"[green]Macro '{macro['name']}' added to keybind '{keybind}'")
    print("[gray]-> Command:", command)


@macros_app.command(name="list", help="List all macros for a keybind")
def macros_list(
    keybind: Annotated[str, typer.Argument(help="Keybind to list macros for")]
):
    data = load_data()
    if keybind not in data:
        print(f"Keybind '{keybind}' not found.")
        raise typer.Abort()

    macros = data[keybind].get("macros", [])

    if not macros:
        print(f"No macros found for keybind '{keybind}'.")
        return

    console = Console()
    table = Table(title=f"Macros for '{keybind}'")
    table.add_column("Index", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Commands", style="green")

    for i, macro in enumerate(macros, 1):
        command_str = " ; ".join(macro["commands"])
        table.add_row(str(i), macro["name"], command_str)

    print(table)

def select_from_list(title: str, options: list[str]) -> str:
    console = Console()
    if not options:
        console.print("[red]No options to choose from.[/red]")
        raise Exception("No options")

    table = Table(show_header=False)
    for i, opt in enumerate(options, 1):
        table.add_row(f"{i}.", opt)
    panel = Panel(Align.center(table), title=title, padding=(1, 2))

    console.clear()
    console.print(panel)

    answer = questionary.select(
        message=f"{title}:",
        choices=options,
        use_arrow_keys=True,
        qmark="▶"
    ).ask()

    console.clear()
    if answer is None:
        raise Exception("No selection made")
    return answer
@app.command(name="run", help="Run a macro from a keybind")
def run_macro(
    keybind: Optional[str] = typer.Argument(None),
    name: Optional[str] = typer.Argument(None),
    args: Optional[List[str]] = typer.Argument(None),
):
    args = args or []

    console = Console()
    data = load_data()

    if not data:
        console.print("[bold red]No macros found.[/bold red]")
        raise typer.Exit()

    if not keybind:
        keybind = select_from_list("Available Keybinds", list(data.keys()))

    if keybind not in data:
        console.print(f"[red]Keybind '{keybind}' not found.[/red]")
        raise typer.Abort()

    macros = data[keybind].get("macros", [])
    if not macros:
        console.print(f"[red]No macros available under keybind '{keybind}'.[/red]")
        raise typer.Exit()

    if not name:
        macro_names = [m["name"] for m in macros]
        name = select_from_list(f"Available Macros for '{keybind}'", macro_names)

    name = sanitize_name(name)
    macro = next((m for m in macros if m["name"] == name), None)
    if not macro:
        console.print(f"[red]Macro '{name}' not found under keybind '{keybind}'.[/red]")
        raise typer.Abort()

    arg_indices = sorted(
        set(int(i) for cmd in macro["commands"] for i in re.findall(r"{(\d+)}", cmd))
    )

    # Falls zu wenig Argumente gegeben, noch abfragen
    while len(args) < len(arg_indices):
        idx = arg_indices[len(args)]
        val = typer.prompt(f"Enter value for argument {{{idx}}}")
        args.append(val)

    console.print()
    console.print(f"[bold green]Executing macro:[/bold green] [cyan]{name}[/cyan]\n[dim]Keybind: {keybind}[/dim]")

    for raw_cmd in macro["commands"]:
        try:
            resolved_cmd = raw_cmd.format(*args)
        except IndexError:
            console.print(f"[red]Missing arguments for command: '{raw_cmd}'[/red]")
            raise typer.Abort()

        console.print(f"[green]→ {resolved_cmd}[/green]")
        result = subprocess.run(resolved_cmd, shell=True)

        if result.returncode != 0:
            console.print(f"[red]Command failed with code {result.returncode}[/red]")
            raise typer.Exit(code=result.returncode)



app.add_typer(keybinds_app, name="keys", help="Manage all available keybinds in Mak.") 
app.add_typer(macros_app, name="maks", help="Manage all Makros in Mak.")
app.add_typer(config_app, name="config", help="Manage Configuration of Mak.")

if __name__ == "__main__":
    app()
