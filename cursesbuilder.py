#  Curses Builder
#  A library for encapsulating curses functions to assist in building
#   curses-backed command-line UIs.
#
#  cursesbuilder.py
#
#  Copyright 2018 James Harmison <jharmison@gmail.com>
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the
#  "Software"), to deal in the Software without restriction, including
#  without limitation the rights to use, copy, modify, merge, publish,
#  distribute, sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so, subject to
#  the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
#  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.


# TODO:
# Subclass message types
# Implement less-like paginator
# Widget-ize processes with scrolling output
# Progress bars! PROGRESS BARS!
# Provide means to encapsulate whole canvasses, drawing widgets on top
#   and eliminating the need to manually wrap curses
# Improve panel handling
# A better menu system that doesn't require class instantiation to chain
#   widgets together
# Handling of multi-line messages

Version = '0.1'

import curses
from curses import panel
from time import sleep
from collections import deque

########################################################################
# Menu class allows for creation of arrow-key-selectable menu choices
#   that perform various actions. Used currently only for main menu,
#   but could be used for submenus, etc.
#
# `items` expected to be a list of 3-tuples.
#   ('Menu entry', action, BreakMenu<True/False>)
########################################################################
class Menu(object):
    def __init__(self, title, subtitle, items, stdscr):
        # Prepare the curses subwindow and panel
        self._window = stdscr.subwin(0,0)
        self._window.keypad(1)
        self._panel = panel.new_panel(self._window)
        self._panel.hide()
        panel.update_panels()

        # Define some variables used by the object's menu
        self._position = 0
        self._title = title
        self._subtitle = subtitle
        self._items = items

    def navigate(self, n):
        # Arrow key handler for selection verifies limits
        self._position += n
        if self._position < 0:
            self._position = 0
        elif self._position >= len(self._items):
            self._position = len(self._items)-1

    def display(self):
        # Bring the curses panel to the top and show it, prepare to draw
        self._panel.top()
        self._panel.show()
        self._window.clear()

        while True:
            # Begin drawing the menu
            self._window.refresh()
            curses.doupdate()
            self._window.addstr(0, 0, self._title, curses.A_BOLD)
            self._window.addstr(1, 0, self._subtitle, curses.A_UNDERLINE)

            # Draw menu options, highlight current position
            for index, item in enumerate(self._items):
                if index == self._position:
                    mode = curses.A_REVERSE
                else:
                    mode = curses.A_NORMAL
                msg = '%d. %s' % (1+index, item[0])
                self._window.addstr(3+index, 1, msg, mode)

            # Wait for input
            key = self._window.getch()

            if key in [curses.KEY_ENTER, ord('\n')]:
                # Break if the third element of this item's 3-tuple
                #   evaluates to True
                if self._items[self._position][2]:
                    break
                # Otherwise, perform the action
                else:
                    self._items[self._position][1]()

            # Handle arrow-key navigation
            elif key == curses.KEY_UP:
                self.navigate(-1)
            elif key == curses.KEY_DOWN:
                self.navigate(1)
            # Validate numeric input, handle
            elif (key - 48) in range(1, 1+len(self._items)):
                self._position = key - 49

        # Following a breaking of the loop, clean the panel/window up.
        self._window.clear()
        self._panel.hide()
        panel.update_panels()
        curses.doupdate()

########################################################################
# InputBox class to build a pop-up text-fill box with granular control
#   over actions, returning the entered string.
#
# Title displayed along the top, default is the pre-filled string,
#   length is the desired width of the text input box, and stdscreen is
#   the parent screen upon which we will draw.
########################################################################
class InputBox(object):
    def __init__(self, title, default, length, stdscreen):
        # We ensure our box will fit on this screen space
        self._maxY, self._maxX = stdscreen.getmaxyx()
        # Aborting if it's really short
        if self._maxY < 3:
            return None

        # Roughly center our input box
        self._startY = int((self._maxY // 2) - (self._maxY % 2) - 1)
        self._endY = int((self._maxY // 2) - (self._maxY % 2) + 1)
        self._length = length
        # Chopping the width to fit the canvas
        if (self._length + 2) >= self._maxX:
            self._length = self._maxX - 2
        self._startX = int((self._maxX // 2) - (self._maxX % 2) - (self._length // 2) - 1)
        self._endX = int((self._maxX // 2) - (self._maxX % 2) + (self._length // 2))

        # Define our subwindow and panel
        self._window = stdscreen.subwin(3, self._length + 2, self._startY, self._startX)
        self._window.keypad(1)
        self._panel = panel.new_panel(self._window)
        self._panel.hide()
        panel.update_panels()

        # Fill the title and default value, chop the value to allow for
        #   cursor moves through string and put the cursor at the end.
        self.title = title
        self.value = default
        self._valueL = default
        self._valueR = ''
        self._curPosition = len(self.value)

    def getVal(self):
        # Display our input box, show the cursor and save the old state
        self._panel.top()
        self._panel.show()
        self._window.clear()
        old_curs = curses.curs_set(1)

        while True:
            # Merge value halves, chop excess length
            self.value = self._valueL + self._valueR
            self.value = self.value[:self._length]
            self._window.refresh()
            curses.doupdate()
            # Draw a box around input dialogue
            self._window.box()
            # Draw title and value
            self._window.addstr(0, 1, self.title, curses.A_BOLD)
            self._window.addstr(1, 1, self.value + (' ' * (self._length - len(self.value) - 1)), curses.A_REVERSE)
            # Put cursor where it belongs
            self._window.move(1, self._curPosition + 1)
            # Wait for input
            key = self._window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                # Save the value
                break
            elif key < 256:
                # Append valueL if able
                if len(self._valueL) < self._length - 1:
                    self._valueL += chr(key)
                    self._curPosition += 1
            elif key == curses.KEY_BACKSPACE:
                # Remove last valueL character if able
                if len(self._valueL) > 0:
                    self._valueL = self._valueL[0:-1]
                    self._curPosition -= 1
            elif key == curses.KEY_DC:
                # Remove first valueR character if able
                if len(self._valueR) > 0:
                    self._valueR = self._valueR[1:]
            elif key == curses.KEY_RIGHT:
                # Shift cursor, and string slices, to the right if able
                if self._curPosition < len(self.value):
                    self._valueL += self._valueR[0]
                    self._valueR = self._valueR[1:]
                    self._curPosition += 1
            elif key == curses.KEY_LEFT:
                # Shift cursor, and string slices, to the left if able
                if self._curPosition > 0:
                    self._valueR = self._valueL[-1]+self._valueR
                    self._valueL = self._valueL[:-1]
                    self._curPosition -= 1

        # After breaking loop, reset cursor style and clean up panel
        curses.curs_set(old_curs)
        self._window.clear()
        self._panel.hide()
        panel.update_panels()
        # Return updated string value
        return self.value

########################################################################
# MessageBox class to display simple messages with different actions.
#
# Title and Message are strings to display, box is dynamically sized and
#   centered. Supports the following methods:
# MessageBox.showMessage()
#   Shows the message and a simple OK button, returns None.
# MessageBox.yesNo()
#   Shows the message with option to select YES or NO, returns True if
#    YES, False if NO
########################################################################
class MessageBox(object):
    def __init__(self, title, message, stdscreen):
        # We ensure our box will fit on this screen space
        self._maxY, self._maxX = stdscreen.getmaxyx()
        # Abort if there's not enough vertical space
        if self._maxY < 4:
            return None
        # Otherwise center
        self._startY = int((self._maxY // 2) - (self._maxY % 2) - 1)
        self._endY = int((self._maxY // 2) - (self._maxY % 2) + 2)
        # Set length and center
        self._length = max(len(title)+1, len(message), 9)
        # Truncate length based on display
        if (self._length + 2) >= self._maxX:
            self._length = self._maxX - 2
        self._startX = int((self._maxX // 2) - (self._maxX % 2) - (self._length // 2) - 1)
        self._endX = int((self._maxX // 2) - (self._maxX % 2) + (self._length // 2))
        # Build window an panel
        self._window = stdscreen.subwin(4, self._length + 2, self._startY, self._startX)
        self._window.keypad(1)
        self._panel = panel.new_panel(self._window)
        self._panel.hide()
        panel.update_panels()
        # Set object's title and message
        self.title = title
        self.message = message

    def showMessage(self):
        # display our panel and clear the window
        self._panel.top()
        self._panel.show()
        self._window.clear()

        while True:
            # Update the curses window
            self._window.refresh()
            curses.doupdate()
            # Draw a box around the window
            self._window.box()
            # Add our title and message, OK button
            self._window.addstr(0, 1, self.title, curses.A_BOLD)
            self._window.addstr(1, 1, self.message)
            self._window.addstr(2, self._length - 4, ' OK ', curses.A_REVERSE)
            # Wait for input
            key = self._window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                # Enter exits pane
                break
            else:
                # Flash the OK button if they press anything other than
                #   enter.
                self._window.addstr(2,self._length - 4, ' OK ', curses.A_NORMAL)
                self._window.refresh()
                curses.doupdate()
                sleep(0.1)
        # Clean up the window/panel
        self._window.clear()
        self._panel.hide()
        panel.update_panels()

    def yesNo(self):
        # display our panel and clear the window
        self._panel.top()
        self._panel.show()
        self._window.clear()

        selected = curses.A_REVERSE
        deselected = curses.A_NORMAL
        selection = deque([selected,deselected])

        while True:
            # Update the curses window
            self._window.refresh()
            curses.doupdate()
            # Draw a box around the window
            self._window.box()

            # Add our title, message, and YES/NO buttons
            self._window.addstr(0, 1, self.title, curses.A_BOLD)
            self._window.addstr(1, 1, self.message)
            self._window.addstr(2, self._length - 4, ' NO ', selection[0])
            self._window.addstr(2, self._length - 9, ' YES ', selection[1])

            # Wait for input
            key = self._window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                if selection.index(selected):
                    returnCode = True
                else:
                    returnCode = False
                break
            elif key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_UP]:
                selection.reverse()
            elif key in [ord('y'),ord('Y')]:
                returnCode = True
                break
            elif key in [ord('n'),ord('N')]:
                returnCode = False
                break

        # Clean up the window/panel
        self._window.clear()
        self._panel.hide()
        panel.update_panels()

        return returnCode
