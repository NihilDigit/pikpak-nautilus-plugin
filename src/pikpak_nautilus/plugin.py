import subprocess
import gi
gi.require_version('Nautilus', '4.0')
from gi.repository import Nautilus, GObject, Gio

class PikPakMenuProvider(GObject.Object, Nautilus.MenuProvider):
    def __init__(self):
        super().__init__()

    def _submit(self, url):
        if not url: return
        # 直接使用 rclone backend，因为它最稳定
        subprocess.Popen(['rclone', 'backend', 'addurl', 'pikpak:', '/', url])
        subprocess.run(['notify-send', 'PikPak', f'Task submitted: {url[:30]}...'])

    def _on_paste_clicked(self, menu, window):
        try:
            # 支持 Wayland (wl-paste) 和 X11 (xclip)
            cmd = ['wl-paste'] if subprocess.run(['which', 'wl-paste'], capture_output=True).returncode == 0 else ['xclip', '-o', '-sel', 'clip']
            url = subprocess.check_output(cmd).decode('utf-8').strip()
            self._submit(url)
        except Exception as e:
            subprocess.run(['notify-send', 'PikPak Error', str(e)])

    def get_background_items(self, *args):
        item = Nautilus.MenuItem(
            name="PikPak::PasteMagnet",
            label="PikPak: Paste Magnet Link",
            tip="Submit magnet link from clipboard to PikPak"
        )
        item.connect("activate", self._on_paste_clicked, args[-1])
        return [item]

    def get_file_items(self, *args):
        # 暂时留空，可以后续扩展右键磁力文件
        return []
