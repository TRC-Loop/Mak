# Installation Guide

The install scripts are also used for updating.
They'll install the latest version available.

## Prerequisites

Make sure the following tools are installed and accessible:

* [Git](https://github.com/git-guides/install-git)
* [Python](https://realpython.com/installing-python/) ≥3.10 (3.10 or higher)
* [pip](https://pip.pypa.io/en/stable/installation/) (comes with Python)
* [curl](https://curl.se) (MacOS/Linux; Windows uses PowerShell's Invoke-WebRequest)

### Verify Prerequisites

=== "Windows"

    ```powershell
    git --version
    python --version
    ```

=== "MacOS/Linux"

    ```bash
    git --version
    python3 --version
    curl --version
    ```

---

## Installation / Update

*By installing, you agree to the [License](https://github.com/TRC-Loop/Mak?tab=GPL-3.0-1-ov-file#readme)*

=== "Windows"

    ```powershell
    powershell -NoProfile -ExecutionPolicy Bypass -Command "& { iwr -useb https://raw.githubusercontent.com/TRC-Loop/Mak/main/scripts/install.ps1 | iex }"
    ```

=== "MacOS/Linux"

    ```bash
    bash -c "$(curl -fsSL https://raw.githubusercontent.com/TRC-Loop/Mak/main/scripts/install.sh)"
    ```

---

## Uninstallation

=== "Windows"

    ```powershell
    powershell -NoProfile -ExecutionPolicy Bypass -Command "& { iwr -useb https://raw.githubusercontent.com/TRC-Loop/Mak/main/scripts/uninstall.ps1 | iex }"
    ```

=== "MacOS/Linux"

    ```bash
    bash -c "$(curl -fsSL https://raw.githubusercontent.com/TRC-Loop/Mak/main/scripts/uninstall.sh)"
    ```

---

## Additional Notes

* On Windows, ExecutionPolicy Bypass allows the scripts to run without being blocked.
* Configure proxy settings if behind a proxy.
* Installation and uninstall logs are located at:

  * %USERPROFILE%.mak_install.log (Windows)
  * ~/.mak_install.log (MacOS/Linux)
* For manual or advanced usage, you can clone the repository and run scripts directly.
* Try running powershell with administrator on windows or with `sudo` on linux/macos if there are errors.
* During the installation, you may need to enter your password.
