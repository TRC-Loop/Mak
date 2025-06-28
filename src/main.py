"""
This module provides a command-line interface for managing keybinds and macros.
It allows users to add, list, remove keybinds, and create, list, and run macros
associated with these keybinds.
"""

import os
import re
import subprocess
from typing import List, Optional
from typing_extensions import Annotated
import typer
import questionary
from rich import print, get_console
from rich.table import Table
from platformdirs import user_config_dir
import orjson

def sanitize_name(name: str) -> str:
    """
    Sanitizes a given name by replacing spaces and underscores with hyphens,
    removing non-alphanumeric characters (except hyphens), and converting to lowercase.

    Args:
        name (str): The name to sanitize.

    Returns:
        str: The sanitized name.
    """
    # Replace spaces and underscores with hyphens
    name = re.sub(r'[ _]+', '-', name)
    # Remove all non-valid characters (keep alphanum, hyphen)
    name = re.sub(r'[^a-zA-Z0-9\-]', '', name)
    # Lowercase
    return name.lower()


VERSION = (1, 0, 0)

DEV_DEBUG_MODE = os.getenv("MAK_DEBUG_MODE", "False").lower() == "true"
APP_NAME = os.getenv("MAK_APP_NAME", "TRCLoop/Mak")
CONFIG_NAME = os.getenv("MAK_CONFIG_NAME", "config.json")
DATASTORE_NAME = os.getenv("MAK_DATASTORE_NAME", "data.json")


GITHUB_LINK = "https://github.com/TRC-Loop/Mak"
# pylint: disable=line-too-long
ASCII_ART = """
                                                                █████             
                                                               ███████            
      ██████████████████         ███████                       ███████            
     ██████     █████████       ████████                       ███████            
    ██████      █████████      ████████                       ███████             
    ██████      █████████     █████████     ████████████████  █████████████████   
    ██████     ███████████   ███ ██████   ██████    ███████   ████████  ███████   
     ██████    ███████████  ███ ███████  ██████     ███████  ████████   ███████   
              ████ ███████ ████ ███████ ███████    ████████  ███████    ███████   
             █████  ██████████  ██████  ██████     ███████   ███████  ███████     
             ████   █████████  ███████ ███████     ███████  ███████ ███████       
            ████    ████████   ███████ ███████    ███████   ███████ ███████       
          ██████     ██████    ███████  ██████   █████████ ████████  ███████      
       ████████      █████     ███████  ███████  ███████ ███████   █████████    
        █████        ████      ████████   ███████  ███████ ███████     ██████     
                               ████████                                           
                                ████████                                          
                                  ████
"""
# pylint: enable=line-too-long

_config_dir = user_config_dir(APP_NAME)
_config_path = os.path.join(_config_dir, CONFIG_NAME)
_datastore_path = os.path.join(_config_dir, DATASTORE_NAME)

def load_config() -> dict:
    """
    Loads the configuration from the config file.

    Returns:
        dict: The loaded configuration.
    """
    if not os.path.exists(_config_path):
        return {}
    with open(_config_path, 'r', encoding='utf-8') as f:
        return orjson.loads(f.read())

def load_data() -> dict:
    """
    Loads the data from the datastore file.

    Returns:
        dict: The loaded data.
    """
    if not os.path.exists(_datastore_path):
        return {}
    with open(_datastore_path, 'r', encoding='utf-8') as f:
        return orjson.loads(f.read())

def save_config(cfg: dict):
    """
    Saves the given configuration to the config file.

    Args:
        cfg (dict): The configuration to save.
    """
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_path, 'wb') as f:
        f.write(orjson.dumps(cfg, option=orjson.OPT_INDENT_2))

def save_data(data: dict):
    """
    Saves the given data to the datastore file.

    Args:
        data (dict): The data to save.
    """
    os.makedirs(_config_dir, exist_ok=True)
    with open(_datastore_path, 'wb') as f:
        f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

app = typer.Typer()

keybinds_app = typer.Typer()
macros_app = typer.Typer()
config_app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Main entry point for the CLI. Displays info if no subcommand is invoked.
    """
    if ctx.invoked_subcommand is None:
        info()

@app.command(name="version", help="Get Version Info")
def version(
    pure: Annotated[bool, typer.Option("--pure", "-p", "--raw", "-r",
                                       help="Return version only")] = False,
    sparse: Annotated[bool, typer.Option("--sparse", "-s",
                                         help="Show semantic version parts")] = False,
):
    """
    Displays the version information of Mak.
    """
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
    """
    Displays general information about Mak, including version, GitHub link,
    and configuration paths.
    """
    print(ASCII_ART)
    print("Version", ".".join(map(str, VERSION)))
    print("Github", GITHUB_LINK)
    print("Config Path", _config_path)
    print("Datastore Path", _datastore_path)
    print("App Name", APP_NAME)
    print("Debug Mode", DEV_DEBUG_MODE)
    print("For help, use --help")


@keybinds_app.command(name="add", help="Add a new Keybind")
def keybinds_add(keybind: Annotated[str, typer.Argument(help="Keybind name")]):
    """
    Adds a new keybind to the datastore.
    """
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
    """
    Lists all registered keybinds.
    """
    data = load_data()
    keybinds = list(data.keys())

    if not keybinds:
        print("No keybinds found.")
        return

    table = Table(title="Registered Keybinds")
    table.add_column("Index", justify="right", style="cyan")
    table.add_column("Keybind", style="magenta")

    for i, kb in enumerate(keybinds, 1):
        table.add_row(str(i), kb)

    print(table)


@keybinds_app.command(name="remove", help="Remove a Keybind")
def keybinds_remove(keybind: Annotated[str, typer.Argument(help="Keybind to remove")]):
    """
    Removes a keybind from the datastore.
    """
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
    """
    Adds a new macro to an existing keybind.
    """
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
    print(f"[gray]-> Command: {command}")


@macros_app.command(name="list", help="List all macros for a keybind")
def macros_list(
    keybind: Annotated[str, typer.Argument(help="Keybind to list macros for")]
):
    """
    Lists all macros associated with a specific keybind.
    """
    data = load_data()
    if keybind not in data:
        print(f"Keybind '{keybind}' not found.")
        raise typer.Abort()

    macros = data[keybind].get("macros", [])

    if not macros:
        print(f"No macros found for keybind '{keybind}'.")
        return

    table = Table(title=f"Macros for '{keybind}'")
    table.add_column("Index", justify="right", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Commands", style="green")

    for i, macro in enumerate(macros, 1):
        command_str = " ; ".join(macro["commands"])
        table.add_row(str(i), macro["name"], command_str)

    print(table)

def select_from_list(title: str, options: list[str]) -> str:
    """
    Presents a list of options to the user and returns the selected option.

    Args:
        title (str): The title for the selection prompt.
        options (list[str]): A list of strings to present as options.

    Returns:
        str: The selected option.

    Raises:
        Exception: If no options are provided or no selection is made.
    """
    console = get_console()
    if not options:
        console.print("[red]No options to choose from.[/red]")
        raise ValueError("No options")

    answer = questionary.select(
        message=f"{title}:",
        choices=options,
        use_arrow_keys=True,
        qmark="▶"
    ).ask()

    console.clear()
    if answer is None:
        raise ValueError("No selection made")
    return answer

@app.command(name="run", help="Run a macro from a keybind")
def run_macro(
    keybind: Optional[str] = typer.Argument(None, help="The keybind to run."),
    name: Optional[str] = typer.Argument(None, help="The name of the macro to run."),
    args: Optional[List[str]] = typer.Argument(None, help="Arguments for the macro commands."),
):
    """
    Runs a macro associated with a keybind. If keybind or macro name are not provided,
    the user will be prompted to select them.
    """
    args = args or []

    console = get_console()
    data = load_data()

    if not data:
        console.print("[bold red]No macros found.[/bold red]")
        raise typer.Exit()

    if not keybind:
        try:
            keybind = select_from_list("Available Keybinds", list(data.keys()))
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(code=1) from e


    if keybind not in data:
        console.print(f"[red]Keybind '{keybind}' not found.[/red]")
        raise typer.Abort()

    macros = data[keybind].get("macros", [])
    if not macros:
        console.print(f"[red]No macros available under keybind '{keybind}'.[/red]")
        raise typer.Exit()

    if not name:
        macro_names = [m["name"] for m in macros]
        try:
            name = select_from_list(f"Available Macros for '{keybind}'", macro_names)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(code=1) from e


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
    console.print(f"[bold green]Executing macro:[/bold green] [cyan]{name}[/cyan]\n"
                  f"[dim]Keybind: {keybind}[/dim]")

    for raw_cmd in macro["commands"]:
        try:
            resolved_cmd = raw_cmd.format(*args)
        except IndexError as exc:
            console.print(f"[red]Missing arguments for command: '{raw_cmd}'[/red]")
            raise typer.Abort() from exc

        console.print(f"[green]→ {resolved_cmd}[/green]")
        result = subprocess.run(resolved_cmd, shell=True, check=False)

        if result.returncode != 0:
            console.print(f"[red]Command failed with code {result.returncode}[/red]")
            raise typer.Exit(code=result.returncode)


app.add_typer(keybinds_app, name="keys", help="Manage all available keybinds in Mak.")
app.add_typer(macros_app, name="maks", help="Manage all Makros in Mak.")
app.add_typer(config_app, name="config", help="Manage Configuration of Mak.")

if __name__ == "__main__":
    app()
