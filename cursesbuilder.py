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

__version__ = '0.2-dev'
__author__ = 'James Harmison <jharmison@gmail.com>'

import curses
from curses import panel
from collections import deque

class Menu(object):
    '''
    Menu class allows for creation of arrow-key-selectable menu choices
      that perform various actions. Used currently only for main menu,
      but could be used for submenus, etc.

    `items` expected to be a list of 3-tuples, or 2-tuples (assuming False)
      ('Menu entry', action, BreakMenu<True/False>)
      ('Menu entry', action)    # Implying BreakMenu = False)


    > item1 = InputBox(stdscr, 'Receive Input', 'default value', length = 30)
    > item2 = MessageBox(stdscr, 'Display Message', 'The message!')
    >
    > items = []
    > items.append( ('Selection 1: Input', item1.show) )
    > items.append( ('Selection 2: Message', item2.show, False) )
    > items.append( ('Exit Menu', False, True) )
    >
    > Menu(stdscr, 'Title', 'Optional Subtitle', items).show()
    > print('You selected "{}" in Selection 1.'.format(item1.value))
    '''
    def __init__(self, stdscr, title = 'Menu', subtitle = '', items = [ ( 'Exit Menu', False, True ) ]):
        # Prepare the curses subwindow and panel
        self._window = curses.newwin(0,0)
        self._window.keypad(1)
        self._panel = panel.new_panel(self._window)
        self._panel.hide()
        panel.update_panels()

        # Define some variables used by the object's menu
        self._position = 0
        self._title = title
        self._subtitle = subtitle
        # Handily append a soft menu break if you forgot...
        if not True in [ x[2] for x in items if len(x) == 3 ]:
            items.append( ('Exit Menu', False, True) )
        self._items = items

    def _navigate(self, n):
        # Arrow key handler for selection verifies limits
        self._position += n
        if self._position < 0:
            self._position = 0
        elif self._position >= len(self._items):
            self._position = len(self._items)-1

    def show(self):
        '''
        Menu.show() - Displays the menu. Meant to be called at the moment
            you want to bring the menu to the top of the window.
        '''
        # Bring the curses panel to the top and show it, prepare to draw
        curses.curs_set(0)
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
                if len(self._items[self._position]) > 2 and self._items[self._position][2]:
                    break
                # Otherwise, perform the action
                else:
                    self._items[self._position][1]()

            # Handle arrow-key navigation
            elif key == curses.KEY_UP:
                self._navigate(-1)
            elif key == curses.KEY_DOWN:
                self._navigate(1)
            # Validate numeric input, handle
            elif (key - 48) in range(1, 1+len(self._items)):
                self._position = key - 49

        # Following a breaking of the loop, clean the panel/window up.
        self._window.clear()
        self._panel.hide()
        panel.update_panels()
        curses.doupdate()

class _BoxButton(object):
    '''
    Class to build selectable buttons for _ButtonBoxes
    Meant to be overloaded to define new button types.
    '''
    def __init__(self, text = 'OK', selected = False):
        # Some easily modifyable class attributes here, you can instantiate
        #   your own instances with different selection criteria (such as
        #   colors or whatnot)
        self._deselected = {'mode': curses.A_NORMAL, 'name': 'deselected'}
        self._selected = {'mode': curses.A_REVERSE, 'name': 'selected'}
        self._modes = deque( ( self._deselected, self._selected ) )
        # Set some basic properties
        self.text = ' ' + text + ' '
        # Enforce deque rotation for modes
        if selected:
            self._modes.rotate()
        # Selected mode should always be in index 0
        self.mode = self._modes[0]
        self.length = len(self.text)

    # Implemented mostly for laziness
    def __str__(self):
        return self.text.strip()

    # Individual mode selection methods, usable for Boxes with lots of
    #   buttons if you like
    def select(self):
        if self.mode != self._selected:
            self.toggle()
    def deselect(self):
        if self.mode != self._deselected:
            self.toggle()

    # Short and sweet highlight mode toggle
    def toggle(self):
        self._modes.rotate()
        self.mode = self._modes[0]

class _ButtonBox(object):
    '''
    Class to display simple messages with different actions.

    This is a skeleton superclass, designed to give overloaded
        subclasses have the following:
        - center method: Does what it says on the tin, recenters the Box
        - adjust method: Moves the Box by y,x from current position, if able
        - move method: Moves the box to y,x if able
        - title property: Title displayed on the Box
        - message property: Message displayed inside the box, as a list of
            newline-split strings

    Various 'private' properties and methods exist for manipulating in
        your own subclasses.
    '''
    def __init__(self, stdscr, title = 'Box', message = 'Message', buttons = None):
        # Set object's title, message, and buttons
        self.title = title
        self.message = message.split('\n')
        self._buttons = buttons
        # We ensure our box will fit on this screen space
        self._parent = stdscr
        self._maxY, self._maxX = self._parent.getmaxyx()
        self._height = 3 + len(self.message)
        # Abort if there's not enough vertical space
        if self._maxY < self._height:
            return None
        # Set width of box, truncating on window length
        self._buttonWidth = sum([x.length for x in self._buttons])
        messageWidth = max(len(x) for x in self.message)
        self._width = min(self._maxX, max(len(title)+1, messageWidth, self._buttonWidth) + 2)
        # Build window and panel, then hide
        self.center()
        self._window = curses.newwin(self._height, self._width, self._startY, self._startX)
        self._window.keypad(1)
        self._panel = panel.new_panel(self._window)
        self._panel.hide()
        panel.update_panels()

    def _show(self):
        # Display our panel and clear the window
        self._panel.top()
        self._panel.show()
        self._window.clear()

    def _hide(self):
        # Clean up the window/panel
        self._window.clear()
        self._panel.hide()
        panel.update_panels()

    def _update(self):
        # Update the curses window
        self.adjust()
        panel.update_panels()
        self._window.refresh()
        curses.doupdate()
        # Draw a box around the window
        self._window.box()
        # Add our title, message, and buttons
        self._window.addstr(0, 1, self.title, curses.A_BOLD)
        for i, m in enumerate(self.message):
            self._window.addstr(1+i, 1, m)
        offset = -1
        for button in self._buttons:
            y = self._height - 2
            x = self._width - self._buttonWidth + offset
            self._window.addstr(y, x, button.text, button.mode['mode'])
            offset += button.length

    def center(self):
        '''
        Centers the panel within the parent
        '''
        self._maxY, self._maxX = self._parent.getmaxyx()
        self._startY = max(0, int((self._maxY // 2) - (self._maxY % 2) - (self._height // 2) - 1))
        self._startX = max(0, int((self._maxX // 2) - (self._maxX % 2) - (self._width // 2) - 1))

    def adjust(self, y = 0, x = 0):
        '''
        Move the panel by amounts y, x from current position with
            some bounds checking to keep in the parent window
        '''
        self._maxY, self._maxX = self._parent.getmaxyx()
        if self._startY + self._height + y < self._maxY:
            self._startY += y
        else:
            self._startY = self._maxY - self._height
        if self._startX + self._width + x < self._maxX:
            self._startX += x
        else:
            self._startX = self._maxX - self._width
        self._startY = max(0, self._startY)
        self._startX = max(0, self._startX)
        self._panel.move(self._startY, self._startX)

    def move(self, y = 0, x = 0):
        '''
        A bit of a hack, but adjust the window's position starting
            from the top left. Bounds check once, cut twice?
        '''
        self._maxY = 0
        self._maxX = 0
        self.adjust(y = y, x = x)

class _SelectionItem(_BoxButton):
    '''
    Private class to allow for selectable items, similar to buttons
        Set indicator to 0 for x-ballots, 1 for check-ballots, or 3 for radial
        toggles. Displayed indictor will be dependant on mode (selected or
        deselected)
    '''
    def __init__(self, text = 'Item', indicator_selected = False, selected = False, indicator = 0):
        indicator_x = ('☐', '☒')
        indicator_check = ('☐', '☑')
        indicator_radial = ('○', '◉')
        indicators = (indicator_x, indicator_check, indicator_radial)
        # Force our indicator into a viable mode
        if indicator not in range(len(indicators)):
            indicator = 0
        self._indicator = indicators[indicator]
        # Save unformatted text for this item
        self._text = text
        # Modify the text with indicator prior to _BoxButton init
        text = self._indicator[indicator_selected] + ' ' + text
        # Call _BoxButton init
        super().__init__(text = text, selected = selected)

    def __str__(self):
        return self._text

    def select(self):
        '''
        Change the indicator to selected
        '''
        # By overloading select, we change the behavior to be unrelated to
        #   highlighting, and instead modify our indicators
        self.text = ' ' + self._indicator[1] + ' ' + self._text + ' '
    def deselect(self):
        '''
        Change the indicator to deselected
        '''
        # The same is done with deselect
        self.text = ' ' + self._indicator[0] + ' ' + self._text + ' '

class _SelectionBox(_ButtonBox):
    '''
    Superclass to allow for selection of options from a list of choices

    `items` should be passed as an iterable of only the entries you want  to be
        displayed
    '''
    def __init__(self, stdscr, title = 'Title', message = 'Message', indicator = 0, items = ['One', 'Two']):
        # Default to an OK/Cancel button
        buttons = [
            _BoxButton(text = 'Cancel'),
            _BoxButton(selected = True)
        ]
        self._items = [ _SelectionItem(text = item, indicator = indicator ) for item in items ]
        self._items[0].toggle()
        self._itemStart = len(message.split('\n')) + 1
        # Make our message big enough to house all our items
        message += ' \n' * (len(items) + 2)
        message += ' ' * max(len(item) for item in items)
        # value stores the returned selection, if called
        self.value = False
        # Initialize our box
        super().__init__(stdscr, title = title, message = message, buttons = buttons)

    def _move(self, direction = None):
        # Allows calling _move() to toggle buttons alone
        if direction is None:
            for button in self._buttons:
                button.toggle()
        else:
            # If direction is positive, go down our indexed _items
            if direction > 0:
                # Iterate to allow changing within indexes, skipping last item
                for i in range(len(self._items) - 1):
                    # Conditional fails if they're trying to go down from last index position
                    if self._items[i].mode == self._items[i]._selected:
                        # Toggle the previously selected item highlight off
                        self._items[i].toggle()
                        try:
                            # See if our range allows us to target a toggle
                            self._items[i + direction].toggle()
                        except IndexError:
                            # If it's out of range, just toggle the last element
                            self._items[-1].toggle()
                        finally:
                            # Quit while you're ahead
                            break
            else:
                # Iterate again, skipping the first item this time
                for i in range(1, len(self._items)):
                    if self._items[i].mode == self._items[i]._selected:
                        # Toggle the previously selected item highlight off
                        self._items[i].toggle()
                        try:
                            # Once again, try to target a toggle
                            self._items[i + direction].toggle()
                        except IndexError:
                            # If out of bounds, just toggle the first item's highlight
                            self._items[0].toggle()
                        finally:
                            break

    def show(self):
        '''
        Display _SelectionBox, enable the following controls:
            - space calls _itemSelect to allow for subclass behavior
            - Up/Down arrows cycle through items vertically
            - Home/End return to top/bottom of item list
            - Left/Right arrows cycle between OK/Cancel buttons
            - Enter selects OK/Cancel

        Method returns False if cancelled, subclassed _itemReturn if True
        '''
        self._show()
        # Set up to allow cancelling selection
        returnCode = False
        # Loop forever
        while True:
            # Draw window updates
            self._update()
            # Add our items
            for index, item in enumerate(self._items):
                self._window.addstr(self._itemStart + index, 2, item.text, item.mode['mode'])
            # Listen for keypress
            key = self._window.getch()
            # Enter selects a button (OK/Cancel)
            if key in [curses.KEY_ENTER, ord('\n')]:
                for button in self._buttons:
                    # If they selected OK, that's a positive result
                    if button.mode == button._selected and str(button) == 'OK':
                        returnCode = True
                        break
                # If they didn't select OK, but did hit enter, they chose to cancel
                break
            # Left and right keys toggle button highlight
            elif key in [ curses.KEY_LEFT, curses.KEY_RIGHT ]:
                self._move()
            # Down key moves our highlight to the next selection item
            elif key == curses.KEY_DOWN:
                self._move(direction = 1)
            # Up key moves our highlight to the last selection item
            elif key == curses.KEY_UP:
                self._move(direction = -1)
            # Home key goes to the top
            elif key == curses.KEY_HOME:
                self._move(direction = -len(self._items))
            # End key to the bottom
            elif key == curses.KEY_END:
                self._move(direction = len(self._items))
            elif chr(key) == ' ':
                # Allow different selection types from subclasses
                self._itemSelect()
        # Clean up our window
        self._hide()
        # Return subclassed selection method if OK, False otherwise
        if returnCode:
            return self._itemReturn()
        else:
            self.value = False
            return False

class SingleSelectionBox(_SelectionBox):
    '''
    Subclass to allow for selection of a single item from a list of choices
    '''
    def __init__(self, stdscr, title = 'Radio Button Box',
      message = 'Select an entry with space,\nselect OK or Cancel with Enter',
      items = [ 'Entry 1', 'Entry 2' ]):
        super().__init__(stdscr, title = title, message = message, indicator = 2, items = items)
        # Set our first item to default to selected
        self._items[0].select()

    def show(self):
        '''
        Display SingleSelectionBox, enable the following controls:
            - space selects a single item and deselects all others
            - Up/Down arrows cycle through items vertically
            - Home/End return to top/bottom of item list
            - Left/Right arrows cycle between OK/Cancel buttons
            - Enter selects OK/Cancel

        Method returns False if cancelled, text of the selected entry if 'OK'
        Also sets value to the same
        '''
        # Just replacing the docstring for the superclassed show()
        super().show()

    def _itemSelect(self):
        # Called when someone presses spacebar in show()
        for item in self._items:
            # Item mode refers to the current highlight
            if item.mode == item._selected:
                # Toggle the highlighted item's indicator on
                item.select()
            else:
                # Toggle any un-highlighted items' indicators off
                item.deselect()

    def _itemReturn(self):
        # Called when show is returned with 'OK'
        for item in self._items:
            # Just iterate through our items, if the indicator is on
            if item.text[1] == item._indicator[1]:
                # Set value and return the unformatted text
                self.value = item._text
                return item._text
        # Failsafe in case we weirdly don't have a selected item
        return False

class MultiSelectionBox(_SelectionBox):
    '''
    Subclass to allow for selection of multiple items from a list of choices
    '''
    def __init__(self, stdscr, title = 'Check-box Button Box',
      message = 'Select an entry with space,\nselect OK or Cancel with Enter',
      items = [ 'Entry 1', 'Entry 2' ]):
        super().__init__(stdscr, title = title, message = message, indicator = 1, items = items)

    def show(self):
        '''
        Display MultiSelectionBox, enable the following controls:
            - space toggles selection of the currently highlighted item
            - Up/Down arrows cycle through items vertically
            - Home/End return to top/bottom of item list
            - Left/Right arrows cycle between OK/Cancel buttons
            - Enter selects OK/Cancel

        Method returns False if cancelled, list of all selected texts if 'OK'
            (In the case of nothing selected, will return an empty list, not
            False, to allow for `if box.show() is not False` type of behavior)
        Also sets value to the same
        '''
        # Just replacing the docstring for the superclassed show()
        super().show()

    def _itemSelect(self):
        # Called when someone presses spacebar in show()
        for item in self._items:
            # Item mode refers to the current highlight
            if item.mode == item._selected:
                # Toggle the highlighted item's indicator on
                if item.text[1] == item._indicator[1]:
                    item.deselect()
                else:
                    item.select()
                # We can break our loop early here
                break

    def _itemReturn(self):
        # Called when show is returned with 'OK'
        returnList = []
        for item in self._items:
            # Just iterate through our items, if the indicator is on
            if item.text[1] == item._indicator[1]:
                # append the text to our list
                returnList.append(item._text)
        # Set our value and return the list of selected items
        self.value = returnList
        return returnList

class MessageBox(_ButtonBox):
    '''
    Subclass to display a simple OK button on a _ButtonBox

    > MessageBox(curses_stdscr, "The Title", "The message.").show()
    '''
    def __init__(self, stdscr, title = 'Message:', message = 'Press OK'):
        # _BoxButton set to default to ' OK ', so this is easy
        buttons = [
            _BoxButton(selected = True)
        ]
        # Call the _ButtonBox __init__()
        super().__init__(stdscr, title, message, buttons)

    def show(self):
        '''
        Display MessageBox, wait for enter.
        '''
        self._show()
        while True:
            self._update()
            # Wait for input
            key = self._window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                # Enter exits the box
                break
        # Clean up our MessageBox
        self._hide()


class YesNoBox(_ButtonBox):
    '''
    Subclass to display YES and NO buttons, allowing arrow keys
        to toggle the selections and Y or N keys to hard select them.

    > i_should_do_it = YesNoBox(curses_stdscr, 'The Title', 'Should I do it?').show()
    > if i_should_do_it:
    >     print('Will do!')
    > else:
    >     print("Alright, I won't!")
    '''
    def __init__(self, stdscr, title = 'Select:', message = 'Yes or no?'):
        # Define our buttons using our built-in selectors from the
        #   superclass.
        buttons = [
            _BoxButton(text = 'YES'),
            _BoxButton(text = 'NO', selected = True)
        ]
        # Call the _ButtonBox __init__()
        super().__init__(stdscr, title, message, buttons)

    def _move(self):
        # Since our choices are binary, we can just toggle them all
        #   on any movement.
        for button in self._buttons:
            button.toggle()

    def show(self):
        '''
        Displays YesNoBox, allows for arrow keys to select between "Yes"
            and "No". Returns True/False
        '''
        self._show()
        returnCode = False
        while True:
            self._update()
            # Wait for input
            key = self._window.getch()
            if key in [curses.KEY_ENTER, ord('\n')]:
                # Binary choices make this easy
                for button in self._buttons:
                    if button.mode == button._selected and str(button) == 'YES':
                        returnCode = True
                        break
                break
            elif key in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_UP]:
                self._move()
            # key handling to allow hard-selection
            elif key in [ord('y'),ord('Y')]:
                returnCode = True
                break
            elif key in [ord('n'),ord('N')]:
                break
        # Clean up our YesNoBox and return the selected choice
        self._hide()
        return returnCode

class InputBox(_ButtonBox):
    '''
    Subclass to display a fillable field with an OK button

    value property: Contains the value for the field, retrievable after
        show() but persistent after __init__

    > the_input = InputBox(curses_stdscr, 'The Title', "the default value", 30)
    > the_input.show()
    > print('You input:', the_input.value)

        OR

    > the_input = InputBox(curses_stdscr, 'The Title', "the default value", 30).show()
    > print('You input:', the_input)
    '''
    def __init__(self, stdscr, title = 'Input:', default = '', length = 20):
        # Define a simple OK button
        buttons = [
            _BoxButton(selected = True)
        ]
        # Fake out the _ButtonBox to give us three lines, 1 space wider
        #   than the passed length
        super().__init__(stdscr, title, ' ' * (length+1) + '\n \n ', buttons)

        # Initialize value, _length, and our split _value variables.
        #   Define _curPosition at the end of value
        self.value = default
        self._length = length
        self._valueL = default
        self._valueR = ''
        self._curPosition = len(self.value)

    def _moveCurs(self, pos = 0, trim = 0, app = None):
        # Move the cursor by pos, optionally removing trim characters
        #   from _valueL (if neg) or _valueR (if pos) or appending app
        #   to _valueL (inserting it at the current cursor position)
        if app and len(self.value) < self._length:
            # Append and shift
            pos = 1
            self._valueL += app[0]
        elif trim == -1:
            # Remove from end of _valueL
            if len(self._valueL) > 0:
                pos = -1
                self._valueL = self._valueL[0:-1]
            else:
                pos = 0
        elif trim == 1:
            # Remove from beginning of _valueR
            if len(self._valueR) > 0:
                pos = 0
                self._valueR = self._valueR[1:]
            else:
                pos = 0
        elif trim == 0:
            # We're just shifting
            if pos < 0:
                # Slide from left to right
                self._valueR = self._valueL[pos:] + self._valueR
                self._valueL = self._valueL[:pos]
            if pos > 0:
                # Slide from right to left
                self._valueL += self._valueR[:pos]
                self._valueR = self._valueR[pos:]
        else:
            # wat
            pos = 0
        # Concatenate and trim value to length
        self.value = ''.join((self._valueL, self._valueR))[:self._length+1]
        # Set cursor position, bounds check it
        self._curPosition += pos
        if self._curPosition < 0:
            self._curPosition = 0
        elif self._curPosition > len(self.value):
            self._curPosition = len(self.value)

    def show(self):
        '''
        Display our InputBox and store the value when they press enter
        '''
        self._show()
        old_curs = curses.curs_set(1)
        while True:
            self._update()
            # This will highlight our field in A_REVERSE through the end
            self._window.addstr(2, 1, self.value + (' ' * (self._length - len(self.value))), curses.A_REVERSE)
            # Put the cursor where it belongs
            self._window.move(2, self._curPosition + 1)
            # Wait for input
            key = self._window.getch()
            # Handle input appropriately
            if key in [curses.KEY_ENTER, ord('\n')]:
                # Accept value, break loop
                break
            elif key < 256:
                # Key was in UTF-8 range, append it
                self._moveCurs(app = chr(key))
            elif key == curses.KEY_BACKSPACE:
                self._moveCurs(trim = -1)
            elif key == curses.KEY_DC:
                self._moveCurs(trim = 1)
            elif key == curses.KEY_RIGHT:
                self._moveCurs(pos = 1)
            elif key == curses.KEY_LEFT:
                self._moveCurs(pos = -1)
            elif key == curses.KEY_HOME:
                self._moveCurs(pos = -self._length)
            elif key == curses.KEY_END:
                self._moveCurs(pos = self._length)

        # After breaking loop, reset cursor style and clean up panel
        curses.curs_set(old_curs)
        self._hide()
        # Return updated string value (useful? maybe ditch this)
        return self.value
