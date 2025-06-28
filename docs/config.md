# Configuration

## Enviroment Variables

### Set Enviroment Variables

=== "Windows Powershell"
    ```powershell
    [Environment]::SetEnvironmentVariable("<name>", "<value>", "User")
    ```

=== "MacOS/Linux"
    ```bash
    export <name>="<value>"
    ```
    You may need to reload the shell configuration:

    ```bash
    source ~/.bashrc
    ```
    ```bash
    source ~/.zshrc
    ```
