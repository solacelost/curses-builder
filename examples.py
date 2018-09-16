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
from time import sleep

########################################################################
# Variables that exist outside of the curses wrapper, or are passed
#   there, are required for intra-curses communication. Really the best
#   way to handle this is wish threading, but that's outside of the
#   scope of this demo (for now)
radio_selection = False
check_selection = False


class chainInputMessage(object):
    '''
    Currently, classes are the best way to handle chaining objects within
    a menu, because the menu doesn't allow args to be passed to
    subordinate functions/classes, so they need initialized prior to
    entry into a menu
    '''
    def __init__(self, stdscr, title='Title', default='', width=20):
        # Setting our value to boolean False allows us to determine if
        #   input was confirmed
        self.value = False
        # We need to save our stdscr because we have to pass it to
        #   another object in display(), rather than instantiate our own
        self._stdscr = stdscr
        # We can instantiate our InputBox now because the content isn't
        #   dynamic after chain object instantiation
        self._inputBox = cur.InputBox(stdscr, title, default, width)

    def display(self):
        # Save the InputBox value into a temporary variable prior to
        #   confirmation
        tempVal = self._inputBox.show()
        # Get confirmation from a Yes/No dialog
        if cur.YesNoBox(self._stdscr,
                        'Confirm your selection?',
                        tempVal).show():
            # Set value, no need to return
            self.value = tempVal


class messageBoxMover(cur.MessageBox):
    '''
    This small subclass of our MessageBox class (also a subclass...)
    enables us to easily move a box around. There are exposed methods
    in the class to do the movement, but no neat way to animate it live.
    '''
    # I don't bother rebuilding __init__ here, I stick with a basic
    #   MessageBox. I do need to replace show(), however...
    def show(self):
        self._show()
        while True:
            self._update()
            # A little iterator to move our box 10 to the right
            for i in range(1, 10):
                # Using adjust() keeps our existing bounds checking in
                #   place.
                self.adjust(x=1)
                # We need to refresh after every adjust()
                self._update()
                sleep(0.1)
            # Tear the box down when user presses Enter
            key = self._window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                break
        self._hide()


def examples(stdscr):
    # Set our title/subtitle
    title = 'Curses Builder Examples, v' + cur.__version__
    subtitle = 'Main Menu Options'

    # Define our InputBox/MessageBox chained object
    chainInput = chainInputMessage(stdscr, 'Enter input:', 'default message')

    # Some other meny entry items
    radioButton = cur.SingleSelectionBox(stdscr, 'Radio-button box',
                                         items=[
                                             'Selection 1',
                                             'Selection 2',
                                             'Selection 3',
                                             'Selection 4'
                                             ])

    # You can just accept defaults for demo purposes, too, or wrap them
    #   with your own defaults if you like
    checkBoxes = cur.MultiSelectionBox(stdscr)

    # Define Menu object items list
    #   ('Entry', action, booleanForSoftBreak)
    menuItems = [
        ('Input Example', chainInput.display),
        ('Radio-button Example', radioButton.show),
        ('Checkbox Selection Example', checkBoxes.show),
        ('Soft menu break', False, True),
        ('Hard exit', exit)
    ]

    # Define the Menu
    menu = cur.Menu(stdscr, title, subtitle, menuItems)
    # Initiate interaction with menu
    menu.show()

    # Menu should be clear, we can act on value of chained input here
    if chainInput.value:
        cur.MessageBox(stdscr, 'You selected:',
                       '"' + chainInput.value + '"').show()
    else:
        # Demo our custom subclass here
        messageBoxMover(stdscr, 'Warning',
                        ("You didn't select a value in the input example!"
                         "There is no need to be upset.")).show()

    # Handling of the UI's selections isn't limited to curses behavior,
    #   you can do whatever you want with it afterwards
    global radio_selection
    global check_selection
    radio_selection = radioButton.value
    check_selection = checkBoxes.value


if __name__ == '__main__':
    # You should definitely use curses.wrapper() to generate your standard
    #   screen. Failure to do so results in a broken terminal unless you
    #   implement your own try/except to clean up, but why do that when
    #   wrapper exists?
    curses.wrapper(examples)

    # Outside of our curses wrapper, we can resume normal print activity in the
    #   shell. This is to demo communication between the curses shell and
    #   "Important Work" outside of it.
    if radio_selection is not False or check_selection is not False:
        for line in ['I see you also tried out our selection boxes.',
                     "Here's what you picked:", '',
                     'Radio selection: {}'.format(radio_selection),
                     'Checkbox selection: {}'.format(check_selection)]:
            print(line)
    else:
        print('Try out the selection boxes next time!')
