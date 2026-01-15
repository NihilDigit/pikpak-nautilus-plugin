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

    def get_background_items(self, *args):
        item = Nautilus.MenuItem(
            name="PikPak::AddLink",
            label="PikPak: Add Download Link",
            tip="Add magnet link or download URL to PikPak"
        )
        item.connect("activate", self._on_add_link_clicked)
        return [item]

    def get_file_items(self, *args):
        return []
