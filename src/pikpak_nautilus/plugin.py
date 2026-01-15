import subprocess
import os
import gi
gi.require_version('Nautilus', '4.1')
from gi.repository import Nautilus, GObject

DIALOG_SCRIPT = os.path.join(os.path.dirname(__file__), 'dialog.py')


class PikPakMenuProvider(GObject.Object, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()

    def _on_add_link_clicked(self, menu, *args):
        subprocess.Popen(
            ['python3', DIALOG_SCRIPT, '--submit'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def _on_refresh_clicked(self, menu, *args):
        # Using a shell script via Popen to keep it non-blocking and show notifications
        script = (
            'notify-send "Rclone" "Refreshing directory cache..." && '
            'rclone rc vfs/refresh recursive=true --fast-list && '
            'notify-send "Rclone" "Cache refresh complete."'
        )
        subprocess.Popen(["bash", "-c", script])

    def get_background_items(self, *args):
        items = []
        
        add_link_item = Nautilus.MenuItem(
            name="PikPak::AddLink",
            label="PikPak: Add Download Link",
            tip="Add magnet link or download URL to PikPak"
        )
        add_link_item.connect("activate", self._on_add_link_clicked)
        items.append(add_link_item)

        refresh_item = Nautilus.MenuItem(
            name="PikPak::RefreshCache",
            label="Rclone: Refresh Cache",
            tip="Refresh rclone directory cache (SIGHUP)"
        )
        refresh_item.connect("activate", self._on_refresh_clicked)
        items.append(refresh_item)

        return items

    def get_file_items(self, *args):
        refresh_item = Nautilus.MenuItem(
            name="PikPak::RefreshCacheFile",
            label="Rclone: Refresh Cache",
            tip="Refresh rclone directory cache (SIGHUP)"
        )
        refresh_item.connect("activate", self._on_refresh_clicked)
        return [refresh_item]
