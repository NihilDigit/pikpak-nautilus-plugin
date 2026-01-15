# PikPak Nautilus Plugin

Quickly add magnet links to PikPak directly from your File Manager.

## Installation

Using `uv`:

```bash
uv tool install git+https://github.com/YOUR_USERNAME/pikpak-nautilus-plugin.git
pikpak-nautilus install
nautilus -q
```

## Requirements

- `nautilus-python` (system package, e.g., `sudo pacman -S python-nautilus`)
- `rclone` configured with a remote named `pikpak:`
- `wl-clipboard` (Wayland) or `xclip` (X11)

## Usage

Right-click on empty space in any folder and select **PikPak: Paste Magnet Link**.
