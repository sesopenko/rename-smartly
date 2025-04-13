import gi
import re
import os
import sys
from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class RenameSmartlyApp(Gtk.Window):
    def __init__(self, folder=None):
        super().__init__(title="Rename Smartly")
        self.set_title("Rename Smartly")
        self.set_border_width(10)
        self.set_default_size(600, 400)

        self.instructions = Gtk.Label()
        self.instructions.set_markup(
            "<b>How to use:</b> Use a regular expression with capture groups.\n"
            "Use <tt>$1</tt>, <tt>$2</tt>, etc. in the rename pattern to insert matches.\n"
            "Example: <tt>.*S(\\d+)E(\\d+).*</tt> → <tt>S$1E$2.mkv</tt>"
        )
        self.instructions.set_justify(Gtk.Justification.LEFT)
        self.instructions.set_xalign(0)

        self.folder = Path(folder) if folder else Path.home()

        self.open_button = Gtk.Button(label="Open Folder")
        self.open_button.connect("clicked", self.on_open_folder)

        # Regex Pattern Label and Entry
        self.regex_label = Gtk.Label(label="Regex Pattern")
        self.regex_label.set_xalign(0)

        self.regex_entry = Gtk.Entry()
        self.regex_entry.set_placeholder_text("e.g. .*S(\\d+)E(\\d+).*.mkv")

        # Rename Pattern Label and Entry
        self.target_label = Gtk.Label(label="Rename Pattern")
        self.target_label.set_xalign(0)

        self.target_entry = Gtk.Entry()
        self.target_entry.set_placeholder_text("e.g. S$1E$2.mkv")

        self.file_list = Gtk.ListStore(str, str)
        self.tree_view = Gtk.TreeView(model=self.file_list)

        for i, title in enumerate(["Original Name", "Renamed To"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            self.tree_view.append_column(column)

        self.github_link = Gtk.Label()
        self.github_link.set_markup(
            '<a href="https://github.com/sesopenko/rename-smartly">GitHub: sesopenko/rename-smartly</a>'
        )
        self.github_link.set_xalign(0)

        self.install_script_button = Gtk.Button(label="Install Nautilus Script")
        self.install_script_button.connect("clicked", self.on_install_nautilus_script)

        self.preview_button = Gtk.Button(label="Preview")
        self.preview_button.connect("clicked", self.on_preview)

        self.rename_button = Gtk.Button(label="Rename")
        self.rename_button.connect("clicked", self.on_rename)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.pack_start(self.instructions, False, False, 0)
        box.pack_start(self.open_button, False, False, 0)
        box.pack_start(self.regex_label, False, False, 0)
        box.pack_start(self.regex_entry, False, False, 0)
        box.pack_start(self.target_label, False, False, 0)
        box.pack_start(self.target_entry, False, False, 0)

        box.pack_start(self.preview_button, False, False, 0)
        box.pack_start(self.rename_button, False, False, 0)
        box.pack_start(self.tree_view, True, True, 0)

        box.pack_start(self.github_link, False, False, 6)
        box.pack_start(self.install_script_button, False, False, 0)

        self.add(box)

        if folder != None:
            self.on_preview(None)

    def on_open_folder(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select Folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
            )
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.folder = Path(dialog.get_filename())
            self.on_preview(None)

        dialog.destroy()

    def on_preview(self, button):
        self.file_list.clear()
        regex = self.regex_entry.get_text()
        target = self.target_entry.get_text()

        try:
            pattern = re.compile(regex)
        except re.error as e:
            self.show_error(f"Invalid regex: {e}")
            return

        files = sorted([f for f in self.folder.iterdir() if f.is_file()], key=lambda f: f.name.lower())

        for file in files:
            match = pattern.match(file.name)
            if match:
                new_name = target
                for i, group in enumerate(match.groups(), 1):
                    new_name = new_name.replace(f"${i}", group)
                self.file_list.append([file.name, new_name])
            else:
                self.file_list.append([file.name, ""])

    def on_rename(self, button):
        for row in self.file_list:
            original = row[0]
            new_name = row[1]
            if not new_name:
                continue  # Skip files with no rename target
            src = self.folder / original
            dst = self.folder / new_name
            if src != dst:
                src.rename(dst)
        self.file_list.clear()
        self.on_preview(None)

    def on_install_nautilus_script(self, button):
        target_dir = Path.home() / ".local/share/nautilus/scripts"
        target_dir.mkdir(parents=True, exist_ok=True)

        source = Path("/usr/share/doc/rename-smartly/nautilus-script")
        target = target_dir / "Rename Smartly"

        try:
            target.write_bytes(source.read_bytes())
            target.chmod(0o755)
            self.show_message("Nautilus script installed to:\n" + str(target))
        except Exception as e:
            self.show_error(f"Failed to install Nautilus script:\n{e}")

    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message,
        )
        dialog.run()
        dialog.destroy()

    def show_message(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.run()
        dialog.destroy()


def main():
    folder = None
    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
        if candidate.is_dir():
            folder = candidate
        else:
            print(f"Warning: '{sys.argv[1]}' is not a valid directory. Opening Home instead.")

    app = RenameSmartlyApp(folder)
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    app.present()
    Gtk.main()


if __name__ == "__main__":
    main()
