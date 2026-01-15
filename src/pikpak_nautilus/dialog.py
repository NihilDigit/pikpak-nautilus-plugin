#!/usr/bin/env python3
"""Standalone GTK4 dialog for PikPak link input."""
import argparse
import json
import subprocess
import sys
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, Adw, GLib, Gdk


def get_clipboard():
    """Get clipboard text, supports Wayland and X11."""
    try:
        if subprocess.run(['which', 'wl-paste'], capture_output=True).returncode == 0:
            return subprocess.check_output(['wl-paste'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
        else:
            return subprocess.check_output(['xclip', '-o', '-sel', 'clip'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
    except:
        return ""


def submit_to_pikpak(url, on_complete=None):
    """Submit URL to PikPak. Calls on_complete(success) when done."""
    def do_submit():
        success = False
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
                # Clear cache via RC instantly
                refresh_cmd = 'rclone rc vfs/forget && notify-send "Rclone" "Cache refreshed."'
                subprocess.Popen(['bash', '-c', refresh_cmd])
                success = True
            else:
                error = result.stderr or 'Unknown error'
                subprocess.Popen(['notify-send', 'PikPak Error', error[:100]])
        except subprocess.TimeoutExpired:
            subprocess.Popen(['notify-send', 'PikPak Error', 'Request timed out'])
        except Exception as e:
            subprocess.Popen(['notify-send', 'PikPak Error', str(e)[:100]])

        if on_complete:
            GLib.idle_add(on_complete, success)

    thread = threading.Thread(target=do_submit)
    thread.daemon = True
    thread.start()


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

        self.cancel_btn = Gtk.Button(label="Cancel")
        self.cancel_btn.connect("clicked", self._on_cancel)
        btn_box.append(self.cancel_btn)

        self.submit_btn = Gtk.Button(label="Submit")
        self.submit_btn.add_css_class("suggested-action")
        self.submit_btn.connect("clicked", self._on_submit)
        btn_box.append(self.submit_btn)

        self.spinner = Gtk.Spinner()
        btn_box.append(self.spinner)

        # Auto-fill: use prefill, or check clipboard for magnet link
        if prefill:
            self.entry.set_text(prefill)
            self.entry.set_position(-1)
        else:
            clipboard = get_clipboard()
            if clipboard.startswith('magnet:'):
                self.entry.set_text(clipboard)
                self.entry.set_position(-1)

        self.entry.grab_focus()
        self.connect("close-request", self._on_close)

        # Add keyboard event controller for Esc key (use capture phase)
        key_controller = Gtk.EventControllerKey()
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_controller)

    def set_submit_mode(self, enabled):
        self._submit_mode = enabled

    def _on_paste(self, btn):
        text = get_clipboard()
        if text:
            self.entry.set_text(text)
            self.entry.set_position(-1)

    def _set_loading(self, loading):
        self.entry.set_sensitive(not loading)
        self.submit_btn.set_sensitive(not loading)
        self.cancel_btn.set_sensitive(not loading)
        if loading:
            self.spinner.start()
        else:
            self.spinner.stop()

    def _on_submit_complete(self, success):
        self.get_application().quit()

    def _on_submit(self, *args):
        text = self.entry.get_text().strip()
        if text:
            if self._submit_mode:
                self._set_loading(True)
                submit_to_pikpak(text, self._on_submit_complete)
            else:
                print(text)
                self.get_application().quit()

    def _on_cancel(self, *args):
        self.get_application().set_exit_code(1)
        self.get_application().quit()

    def _on_close(self, *args):
        self.get_application().set_exit_code(1)
        return False

    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle Esc key to close dialog."""
        if keyval == Gdk.KEY_Escape:
            self._on_cancel()
            return True
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
