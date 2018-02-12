# Curses Builder
#### A library for encapsulating curses functions to assist in building curses-backed command-line UIs.

### Usage
---
Currently, no setuptools package is built so you'll just have to put it in either a virtualenv's site-packages folder yourself, or drop it into your project's directory. Then, import as normal.

### TODO:
#### In no particular order...
---
- Subclass message types, make more of them?
- Implement less-like paginator for strings or file content inside a panel
- Widget-ize subprocesses with scrolling output
- Progress bars! PROGRESS BARS!
- Provide means to encapsulate whole canvasses, drawing widgets on top and eliminating the need to manually wrap curses
- Improve panel handling, provide interface for moving panels
- A better menu system that doesn't require class instantiation to chain widgets together
- Handling of multi-line messages

## Classes
### Menu
---
- Constructor: Menu(title, subtitle, items, stdscr)
  - title: String for title of menu, bold
  - subtitle: String for subtitle of menu, underlined
  - item: list, or other iterable, with iterable entries as follows:
    - ('Entry text', wrappable action, Boolean value indicating whether to break the menu)
      - Boolean menu break allows you to customize your own "Continue"
      - Set entry item to `exit` to force a hard quit, if you like
  - stdscr: A curses-initialized window object on which to build the menu
- display method:
  - Initiates menu display immediately
  - Returns nothing

### InputBox
---
- Constructor: InputBox(title, default, length, stdscr)
  - title: String for the title on the input box
  - default: String for the default value to fill the input box
  - length: Integer representing width of space to allow input
  - stdscr: Parent curses window on which to draw subwindow/panel
- getVal method:
  - Spawns InputBox panel on parent stdscr, allows editing until Enter pressed
  - Returns value
- value property:
  - Stores default value until getVal called, stores modified value after
- title property:
  - Stores title used to instantiate the InputBox, so you can create a hash table of questions and answers if you like

### MessageBox
---
- Constructor: MessageBox(title, message, stdscr)
  - title: String for the title on the message box
  - message: String for the message to display
  - stdscr: Parent curses window on which to draw subwindow/panel
- showMessage method:
  - Spawns simple message box panel with OK button
  - Returns nothing
- yesNo method:
  - Spawns message box panel with YES/NO buttons
    - pressing Y or N quick-selects an option
    - Arrow keys move between options
    - Enter selects highlighted option
  - Returns True if YES, False if NO
- title property:
  - Stores title used to instantiate MessageBox
- message property:
  - Stores message used to instantiate MessageBox
