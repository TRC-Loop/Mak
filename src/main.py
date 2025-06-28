"""
This module provides a command-line interface for managing keybinds and macros.
It allows users to add, list, remove keybinds, and create, list, and run macros
associated with these keybinds.
"""

import os
import sys
import re
import subprocess
from typing import List, Optional
from typing_extensions import Annotated
import typer
import questionary
from rich import print, get_console
from rich.table import Table
from rich import text
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


VERSION = (1, 1, 0)

DEV_DEBUG_MODE = os.getenv("MAK_DEBUG_MODE", "False").lower() == "true"
APP_NAME = os.getenv("MAK_APP_NAME", "TRCLoop/Mak")
CONFIG_NAME = os.getenv("MAK_CONFIG_NAME", "config.json")
DATASTORE_NAME = os.getenv("MAK_DATASTORE_NAME", "data.json")
# Global flag to indicate if we're in "shell output mode"
# This is useful so we don't print rich formatting if we're outputting shell commands
SHELL_OUTPUT_MODE = False

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
    shell: Annotated[
        bool, typer.Option("--shell", "-S",
                           help="Output shell commands to stdout. Disables Rich formatting.")
    ] = False,
):
    """
    Runs a macro. When --shell is used, it prints commands for a wrapper script/eval.
    """
    global SHELL_OUTPUT_MODE
    SHELL_OUTPUT_MODE = shell

    args = args or []
    console = get_console()
    # print_func will either be sys.stdout.write (for --shell) or rich.print (normal)
    print_func = sys.stdout.write if SHELL_OUTPUT_MODE else print

    data = load_data()

    if not data:
        # In shell mode, output echo command to stderr for user, and then exit.
        print_func("echo \"No macros found.\"\n" if SHELL_OUTPUT_MODE else "[bold red]No macros found.[/bold red]\n")
        raise typer.Exit(1)

    # --- Interactive Prompts Handling (Crucial for --shell mode) ---
    # Temporarily disable SHELL_OUTPUT_MODE for interactive prompts
    # so rich formatting and questionary work. Re-enable in finally.

    if not keybind:
        _temp_shell_output_mode = SHELL_OUTPUT_MODE
        SHELL_OUTPUT_MODE = False
        try:
            keybind = select_from_list("Available Keybinds", list(data.keys()))
        except ValueError as e:
            print_func(f"echo \"Error: {e}\"\n" if not _temp_shell_output_mode else f"[red]{e}[/red]\n")
            raise typer.Exit(1) from e
        finally:
            SHELL_OUTPUT_MODE = _temp_shell_output_mode

    if keybind not in data:
        print_func(f"echo \"Keybind '{keybind}' not found.\"\n" if SHELL_OUTPUT_MODE else f"[red]Keybind '{keybind}' not found.[/red]\n")
        raise typer.Abort()

    macros = data[keybind].get("macros", [])
    if not macros:
        print_func(f"echo \"No macros available under keybind '{keybind}'.\"\n" if SHELL_OUTPUT_MODE else f"[red]No macros available under keybind '{keybind}'.[/red]\n")
        raise typer.Exit(1)

    if not name:
        _temp_shell_output_mode = SHELL_OUTPUT_MODE
        SHELL_OUTPUT_MODE = False
        macro_names = [m["name"] for m in macros]
        try:
            name = select_from_list(f"Available Macros for '{keybind}'", macro_names)
        except ValueError as e:
            print_func(f"echo \"Error: {e}\"\n" if not _temp_shell_output_mode else f"[red]{e}[/red]\n")
            raise typer.Exit(1) from e
        finally:
            SHELL_OUTPUT_MODE = _temp_shell_output_mode

    name = sanitize_name(name)
    macro = next((m for m in macros if m["name"] == name), None)
    if not macro:
        print_func(f"echo \"Macro '{name}' not found under keybind '{keybind}'.\"\n" if SHELL_OUTPUT_MODE else f"[red]Macro '{name}' not found under keybind '{keybind}'.[/red]\n")
        raise typer.Abort()

    arg_indices = sorted(
        set(int(i) for cmd in macro["commands"] for i in re.findall(r"{(\d+)}", cmd))
    )

    while len(args) < len(arg_indices):
        _temp_shell_output_mode = SHELL_OUTPUT_MODE
        SHELL_OUTPUT_MODE = False
        try:
            idx = arg_indices[len(args)]
            val = typer.prompt(f"Enter value for argument {{{idx}}}")
            args.append(val)
        finally:
            SHELL_OUTPUT_MODE = _temp_shell_output_mode


    # --- End of Interactive Prompts Handling ---

    if not SHELL_OUTPUT_MODE:
        print_func("\n")
        print_func(f"[bold green]Executing macro:[/bold green] [cyan]{name}[/cyan]\n")
        print_func(f"[dim]Keybind: {keybind}[/dim]\n")

    commands_to_execute = [] # This list will hold all resolved commands, ready for printing or sub-process

    for raw_cmd in macro["commands"]:
        try:
            processed_cmd = raw_cmd.format(*args)
        except IndexError as exc:
            error_msg = f"Missing arguments for command: '{raw_cmd}'"
            print_func(f"echo \"{error_msg}\"\n" if SHELL_OUTPUT_MODE else f"[red]{error_msg}[/red]\n")
            raise typer.Abort() from exc
        commands_to_execute.append(processed_cmd)


    if SHELL_OUTPUT_MODE:
        # In shell output mode, just print the commands directly.
        # The mak/mak.cmd launcher will handle the eval/FOR /F.
        for cmd in commands_to_execute:
            # For 'cd' commands, ensure they are output as `cd "path"` for robustness.
            cd_match = re.match(r'^\s*cd\s+("(?P<quoted_path>[^"]+)"|(?P<unquoted_path>\S+))\s*$', cmd)
            if cd_match:
                target_path = cd_match.group("quoted_path") or cd_match.group("unquoted_path")
                print_func(f"cd \"{target_path}\"\n") # Output `cd "path"` directly
            else:
                # For other commands, print them as is.
                # It's assumed simple commands or complex commands that are self-contained.
                print_func(f"{cmd}\n")

    else:
        # In normal mode, execute directly using subprocess
        if commands_to_execute:
            # Join all commands into a single string for execution in one sub-shell
            # Note: This means 'cd' commands here only affect the sub-shell.
            full_shell_command = " && ".join(commands_to_execute)
            print_func(f"\n[green]Executing in sub-shell: {full_shell_command}[/green]\n")
            result = subprocess.run(full_shell_command, shell=True, check=False)

            if result.returncode != 0:
                print_func(f"[red]Sub-shell command failed with code {result.returncode}[/red]\n")
                raise typer.Exit(code=result.returncode)
        else:
            print_func("[dim]No commands to execute.[/dim]\n")

        # Give the hint in normal mode
        print_func(text.Text.assemble(
            "\n[bold yellow]Note:[/bold yellow] ",
            "To change your actual shell's directory, launch 'mak' directly (if installed):\n",
            text.Text("mak run ...\n", style="italic cyan"),
            "If using `python main.py`, you need to `eval` its output:\n",
            text.Text("eval \"$(python main.py run --shell ...)\"\n", style="italic cyan"),
            "Python script's current working directory: ",
            text.Text(os.getcwd(), style="bold blue")
        ))



app.add_typer(keybinds_app, name="keys", help="Manage all available keybinds in Mak.")
app.add_typer(macros_app, name="maks", help="Manage all Makros in Mak.")
app.add_typer(config_app, name="config", help="Manage Configuration of Mak.")

if __name__ == "__main__":
    app()
