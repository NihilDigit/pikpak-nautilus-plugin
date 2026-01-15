# PikPak Nautilus Plugin

Modern GTK4-based Nautilus plugin for adding magnet links and download URLs to PikPak cloud storage.

## Features

- **Nautilus Integration**: Right-click menu in file manager to add download links
- **Browser Integration**: Handle `magnet:` links from any browser
- **App Launcher**: Launch from application menu to manually add links
- **Smart Clipboard**: Auto-detects and prefills magnet links from clipboard
- **Modern GTK4 Dialog**: Clean Adwaita interface with:
  - One-click clipboard paste button
  - Loading spinner during submission
  - Keyboard shortcuts (Enter to submit, Esc to close)
- **Desktop Notifications**: Shows task name and status after submission
- **Async Submission**: Non-blocking rclone backend calls with timeout handling

## Requirements

- **Python 3.11+** with GTK4 bindings
- **nautilus-python**: `sudo pacman -S python-nautilus` (Arch) or equivalent
- **rclone**: Configured with a remote named `pikpak:`
  ```bash
  rclone config create pikpak pikpak
  ```
- **Clipboard tools**: `wl-clipboard` (Wayland) or `xclip` (X11)

## Installation

```bash
# Install with uv
uv tool install git+https://github.com/NihilDigit/pikpak-nautilus-plugin.git

# Set up Nautilus extension and magnet: handler
pikpak-nautilus install

# Restart Nautilus
nautilus -q
```

This installs:
- Nautilus extension loader (`~/.local/share/nautilus-python/extensions/`)
- Desktop entry for `magnet:` URL handler
- Application launcher (shows in app menu)
- Wrapper script (`~/.local/bin/pikpak-add`)
- Icon asset

## Usage

### From Nautilus
Right-click on empty space → **PikPak: Add Download Link**

### From Browser
Click any `magnet:` link → Dialog opens with link prefilled → Press Enter or click Submit

### From App Menu
Search for "PikPak" in your application launcher → Opens dialog to manually input links

### Keyboard Shortcuts
- **Enter**: Submit current URL
- **Esc**: Close dialog

## Architecture

```
┌─────────────────┐
│ Nautilus Plugin │ (plugin.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GTK4 Dialog    │ (dialog.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  rclone backend │ addurl to pikpak:
└─────────────────┘
```

- **Loader**: `pikpak_nautilus_loader.py` adds package to sys.path for Nautilus
- **Plugin**: Registers background menu item using Nautilus.MenuProvider
- **Dialog**: Standalone GTK4/Adwaita window with async submission
- **Wrapper**: `pikpak-add` script for desktop integration

## Troubleshooting

**Plugin not showing in Nautilus:**
- Check `~/.local/share/nautilus-python/extensions/pikpak_nautilus_loader.py` exists
- Verify nautilus-python is installed: `python3 -c "import gi; gi.require_version('Nautilus', '4.1')"`
- Restart Nautilus: `nautilus -q`

**Magnet links not handled:**
- Verify registration: `xdg-mime query default x-scheme-handler/magnet`
  - Should return: `pikpak-handler.desktop`
- Re-run: `pikpak-nautilus install`

**Submission fails:**
- Check rclone config: `rclone listremotes | grep pikpak`
- Test manually: `rclone backend addurl pikpak:My\ Pack <magnet-link>`

## Uninstall

```bash
pikpak-nautilus uninstall
uv tool uninstall pikpak-nautilus-plugin
```

## Development

```bash
# Install in development mode
uv pip install -e .

# Test dialog standalone
python3 src/pikpak_nautilus/dialog.py "magnet:?xt=..."

# Test with submit mode
python3 src/pikpak_nautilus/dialog.py --submit
```

## License

MIT
