import typer
import os
from rich import print
from rich.console import Console
from rich.table import Table
from typing_extensions import Annotated
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

@macros_app.command(name="remove", help="Remove a macro from a keybind")
def macros_remove(
    keybind: Annotated[str, typer.Argument(help="Keybind to remove macro from")],
    name: Annotated[str, typer.Argument(help="Macro name to remove")]
):
    data = load_data()
    if keybind not in data:
        print(f"Keybind '{keybind}' not found.")
        raise typer.Abort()

    macros = data[keybind].get("macros", [])
    name = sanitize_name(name)

    new_macros = [m for m in macros if m["name"] != name]

    if len(new_macros) == len(macros):
        print(f"No macro named '{name}' found under '{keybind}'.")
        raise typer.Abort()

    data[keybind]["macros"] = new_macros
    save_data(data)
    print(f"Macro '{name}' removed from keybind '{keybind}'.")


app.add_typer(keybinds_app, name="keys", help="Manage all available keybinds in Mak.") 
app.add_typer(macros_app, name="maks", help="Manage all Makros in Mak.")
app.add_typer(config_app, name="config", help="Manage Configuration of Mak.")

if __name__ == "__main__":
    app()
