# PikPak Nautilus Plugin

Add magnet links to PikPak directly from Nautilus or your browser.

## Features

- **Nautilus Integration**: Right-click menu to add download links
- **Browser Integration**: Click magnet links in browser to add to PikPak
- **GTK4 Dialog**: Modern dialog with clipboard paste button
- **Notifications**: Shows task name and status after submission

## Installation

```bash
# Install with uv
uv tool install git+https://github.com/NihilDigit/pikpak-nautilus-plugin.git

# Set up Nautilus extension and magnet: handler
pikpak-nautilus install

# Restart Nautilus
nautilus -q
```

## Requirements

- `nautilus-python` (e.g., `sudo pacman -S python-nautilus`)
- `rclone` configured with a remote named `pikpak:`
- `wl-clipboard` (Wayland) or `xclip` (X11)

## Usage

### From Nautilus

Right-click on empty space → **PikPak: Add Download Link**

### From Browser

Click any `magnet:` link → Dialog opens with link prefilled → Submit

## Uninstall

```bash
pikpak-nautilus uninstall
uv tool uninstall pikpak-nautilus-plugin
```
