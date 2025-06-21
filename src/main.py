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

_config_dir = user_config_dir(APP_NAME)
_config_path = os.path.join(_config_dir, CONFIG_NAME)

os.makedirs(_config_path, exist_ok=True)

def load_config():
    if not os.path.exists(_config_path):
        return {}
    with open(_config_path, 'r') as f:
        return orjson.loads(f.read())

def save_config(cfg: dict):
    os.makedirs(_config_dir, exist_ok=True)
    with open(_config_path, 'wb') as f:
        f.write(orjson.dumps(cfg, option=orjson.OPT_INDENT_2))

app = typer.Typer()

keybinds_app = typer.Typer()
macros_app = typer.Typer()
config_app = typer.Typer()


@app.command(name="version", help="Get Version Info", rich_help_panel="Version")
@app.command(name="ver", help="Get Version Info", rich_help_panel="Version")
@app.command(name="v", help="Get Version Info", rich_help_panel="Version")
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


app.add_typer(keybinds_app, name="keys", help="Manage all available keybinds in Mak.", rich_help_panel="Keybinds")
app.add_typer(macros_app, name="maks", help="Manage all Makros in Mak.", rich_help_panel="Makros")
app.add_typer(config_app, name="config", help="Manage Configuration of Mak.", rich_help_panel="Mak Settings")

if __name__ == "__main__":
    app()
