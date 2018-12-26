#!/usr/local/opt/python3/bin/python3.7
import urwid
import subprocess
import sys
import os

class SelectableText(urwid.Text):
    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

class ExtendedListBox(urwid.ListBox):
    def __init__(self, content, select_callback):
        body = urwid.SimpleListWalker(content)
        self.length = len(content)
        self.select_callback = select_callback
        super(ExtendedListBox, self).__init__(body)

    def keypress(self, size, key):
        key = self.__super.keypress(size, key)
        if key == 'j' and self.focus_position < self.length:
            key =  self._keypress_down(size)
        if key == 'ctrl d' and self.focus_position < self.length:
            key =  self._keypress_page_down(size)
        if key == 'k' and self.focus_position > 0:
            key =  self._keypress_up(size)
        if key == 'ctrl u' and self.focus_position < self.length:
            key =  self._keypress_page_up(size)
        self.select_callback(self.focus.base_widget.text)
        return key

def handle_input(input):
    if input == "enter": # Open link
#        focus_widget, idx = content_container.get_focus()
#        url = focus_widget.base_widget.text
#        print(text)
        pass
    elif input in ('q', 'Q'): # Quit
        raise urwid.ExitMainLoop()

def run_command(command_string, parameter):
    p = subprocess.Popen(f"{command_string} '{parameter}'", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return output

command_string = 'cat'
content_items = []

for line in sys.stdin.readlines():
    content_items.append(line.strip())
#sys.__stdin__.close()
#reopen stdin to prevent urwid error
sys.__stdin__ = sys.stdin = open('/dev/tty', 'r')
os.dup2(sys.stdin.fileno(), 0)

text = urwid.Text([run_command(command_string, content_items[0])])
textbox = urwid.Filler(text, valign='top')

def focus_callback(selected_text):
    output = run_command(command_string, selected_text)
    text.set_text(output);

palette = [
  ('menu', 'black', 'dark cyan', 'standout'),
  ('reveal focus', 'black', 'dark cyan', 'standout')]

menu = urwid.Text([
    '\n',
    ('menu', u' ENTER '), ('light gray', u" Open link "),
    ('menu', u' Q '), ('light gray', u" Quit"),
])

listitems = list(map(lambda url: urwid.AttrMap(SelectableText(url), None, "reveal focus"), content_items))

content = urwid.SimpleListWalker(listitems)
listbox = ExtendedListBox(content, focus_callback)

columns = urwid.Columns([listbox, textbox])
frame = urwid.Frame(body=columns, footer=menu)

main_loop = urwid.MainLoop(frame, palette, unhandled_input=handle_input)
main_loop.run()
