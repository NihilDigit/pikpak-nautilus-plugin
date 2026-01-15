#!/usr/bin/env python3
"""Standalone GTK4 dialog for PikPak link input."""
import argparse
import json
import subprocess
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


def submit_to_pikpak(url):
    """Submit URL to PikPak and return result."""
    try:
        result = subprocess.run(
            ['rclone', 'backend', 'addurl', 'pikpak:My Pack', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            name = data.get('file_name', 'Unknown')
            status = data.get('message', 'Submitted')
            subprocess.Popen(['notify-send', 'PikPak', f'{name}\n{status}'])
            return True
        else:
            error = result.stderr or 'Unknown error'
            subprocess.Popen(['notify-send', 'PikPak Error', error[:100]])
            return False
    except subprocess.TimeoutExpired:
        subprocess.Popen(['notify-send', 'PikPak Error', 'Request timed out'])
        return False
    except Exception as e:
        subprocess.Popen(['notify-send', 'PikPak Error', str(e)[:100]])
        return False


class LinkDialog(Gtk.Window):
    def __init__(self, app, prefill=""):
        super().__init__(title="PikPak", application=app)
        self.set_default_size(450, -1)
        self.set_resizable(False)
        self._submit_mode = False

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)
        self.set_child(box)

        label = Gtk.Label(label="Enter magnet link or download URL:")
        label.set_halign(Gtk.Align.START)
        box.append(label)

        entry_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.append(entry_box)

        self.entry = Gtk.Entry()
        self.entry.set_hexpand(True)
        self.entry.set_placeholder_text("magnet:?xt=... or https://...")
        self.entry.connect("activate", self._on_submit)
        if prefill:
            self.entry.set_text(prefill)
            self.entry.set_position(-1)
        entry_box.append(self.entry)

        paste_btn = Gtk.Button()
        paste_btn.set_icon_name("edit-paste-symbolic")
        paste_btn.set_tooltip_text("Paste from clipboard")
        paste_btn.connect("clicked", self._on_paste)
        entry_box.append(paste_btn)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_margin_top(6)
        box.append(btn_box)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", self._on_cancel)
        btn_box.append(cancel_btn)

        submit_btn = Gtk.Button(label="Submit")
        submit_btn.add_css_class("suggested-action")
        submit_btn.connect("clicked", self._on_submit)
        btn_box.append(submit_btn)

        self.entry.grab_focus()
        self.connect("close-request", self._on_close)

    def set_submit_mode(self, enabled):
        self._submit_mode = enabled

    def _get_clipboard_text(self):
        try:
            if subprocess.run(['which', 'wl-paste'], capture_output=True).returncode == 0:
                return subprocess.check_output(['wl-paste'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
            else:
                return subprocess.check_output(['xclip', '-o', '-sel', 'clip'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        except:
            return ""

    def _on_paste(self, btn):
        text = self._get_clipboard_text()
        if text:
            self.entry.set_text(text)
            self.entry.set_position(-1)

    def _on_submit(self, *args):
        text = self.entry.get_text().strip()
        if text:
            if self._submit_mode:
                submit_to_pikpak(text)
            else:
                print(text)
            self.get_application().quit()

    def _on_cancel(self, *args):
        self.get_application().set_exit_code(1)
        self.get_application().quit()

    def _on_close(self, *args):
        self.get_application().set_exit_code(1)
        return False


class App(Adw.Application):
    def __init__(self, prefill="", submit_mode=False):
        super().__init__(application_id="com.pikpak.dialog")
        self._exit_code = 0
        self._prefill = prefill
        self._submit_mode = submit_mode

    def do_activate(self):
        win = LinkDialog(self, self._prefill)
        win.set_submit_mode(self._submit_mode)
        win.present()

    def set_exit_code(self, code):
        self._exit_code = code

    def do_shutdown(self):
        Adw.Application.do_shutdown(self)
        sys.exit(self._exit_code)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', nargs='?', default='', help='URL to prefill')
    parser.add_argument('--submit', action='store_true', help='Submit directly via rclone')
    args = parser.parse_args()

    app = App(args.url, args.submit)
    app.run([])


if __name__ == "__main__":
    main()
