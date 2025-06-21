import typer
import os
from rich import print
from typing_extensions import Annotated
from platformdirs import user_config_dir
import orjson

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

@app.command(name="version", help="Get Version Info", rich_help_panel="Info")
@app.command(name="ver", help="Get Version Info", rich_help_panel="Info")
@app.command(name="v", help="Get Version Info", rich_help_panel="Info")
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

@app.command(name="info", help="Display Info about Mak", rich_help_panel="Info")
def info():
    print(ASCII_ART)
    print("Version",".".join(map(str, VERSION)))
    print("Github", GITHUB_LINK)
    print("Config Path", _config_path)
    print("Datastore Path", _datastore_path)
    print("App Name", APP_NAME)
    print("Debug Mode", DEV_DEBUG_MODE)
    print("For help, use --help")


@keybinds_app.command(name="add", help="Add a new Keybind to list", rich_help_panel="Keybinds")
def keybinds_add(keybind: Annotated[str, typer.Argument(help="Keybind for accessing Makros (Keep it short!)")]):
    data = load_data()

    if keybind in data.get("keybinds", []):
        print("Keybind already exists.")
        raise typer.Abort()

    data.setdefault("keybinds", []).append(keybind)
    save_data(data)
    print(f"Added keybind: {keybind}")

@keybinds_app.command(name="list", help="List all Keybinds", rich_help_panel="Keybinds")
def keybinds_list():
    data = load_data()
    keybinds = data.get("keybinds", [])
    if not keybinds:
        print("No keybinds found.")
    else:
        for kb in keybinds:
            print(kb)

@keybinds_app.command(name="remove", help="Remove a Keybind from list", rich_help_panel="Keybinds")
def keybinds_remove(keybind: Annotated[str, typer.Argument(help="Keybind to remove")]):
    data = load_data()
    keybinds = data.get("keybinds", [])
    if keybind not in keybinds:
        print("Keybind not found.")
        raise typer.Abort()

    keybinds.remove(keybind)
    save_data(data)
    print(f"Removed keybind: {keybind}")

app.add_typer(keybinds_app, name="keys", help="Manage all available keybinds in Mak.", rich_help_panel="Keybinds")
app.add_typer(macros_app, name="maks", help="Manage all Makros in Mak.", rich_help_panel="Makros")
app.add_typer(config_app, name="config", help="Manage Configuration of Mak.", rich_help_panel="Mak Settings")

if __name__ == "__main__":
    app()
