#!/usr/bin/env python3

#  Curses Builder
#  A library for encapsulating curses functions to assist in building
#   curses-backed command-line UIs.
#
#  examples.py
#   Some pre-built examples to show/test functionality
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

import curses
import cursesbuilder as cur

########################################################################
# Currently, classes are the best way to handle chaining objects within
#   a menu, because the menu doesn't allow args to be passed to
#   subordinate functions/classes, so they need initialized prior to
#   entry into a menu
class chainInputMessage(object):
    def __init__(self, title, default, width, stdscr):
        # Setting our value to boolean False allows us to determine if
        #   input was confirmed
        self.value = False
        # We need to save our stdscr because we have to pass it to
        #   another object in display()
        self._stdscr = stdscr
        # We can instantiate our InputBox now because the content isn't
        #   dynamic after object instantiation
        self._inputBox = cur.InputBox(title, default, width, stdscr)

    def display(self):
        # Save the InputBox value into a temporary variable prior to
        #   confirmation
        tempVal = self._inputBox.getVal()
        # Get confirmation from a Yes/No dialog
        if cur.MessageBox('Confirm your selection?', tempVal, self._stdscr).yesNo():
            # Set value, no need to return
            self.value = tempVal


def examples(stdscr):
    # Blank the cursor for menu handling
    curses.curs_set(0)

    # Set our title/subtitle
    title = 'Curses Builder Examples, v' + cur.Version
    subtitle = 'Main Menu Options'

    # Define our InputBox/Message chained object
    chainInput = chainInputMessage('Enter input:', 'default message', 20, stdscr)

    # Define Menu object items list
    #   ('Entry', action, booleanForSoftBreak)
    menuItems = [
        ('Input Example', chainInput.display, False),
        ('Soft menu break', False, True),
        ('Hard exit', exit, False)
    ]

    # Define the Menu
    menu = cur.Menu(title, subtitle, menuItems, stdscr)
    # Initiate interaction with menu
    menu.display()

    # Menu should be clear, we can act on value of chained input here
    if chainInput.value:
        cur.MessageBox('You selected:', chainInput.value, stdscr).showMessage()
    else:
        cur.MessageBox('Warning',"You didn't select a value!",stdscr).showMessage()

if __name__ == '__main__':
    # You should definitely use curses.wrapper() to generate your standard
    #   screen. Failure to do so results in a broken terminal unless you
    #   implement your own try/except to clean up, but why do that when
    #   wrapper exists?
    curses.wrapper(examples)
