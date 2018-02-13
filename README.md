# Curses Builder
#### A library for encapsulating curses functions to assist in building curses-backed command-line UIs.

### Usage
---
Currently, no setuptools package is built so you'll just have to put it in either a virtualenv's site-packages folder yourself, or drop it into your project's directory. Then, import as normal.

example.py demonstrates usage of every primary class, as well as how to create custom subclasses.

### TODO:
#### In no particular order...
---
- Implement less-like paginator for strings or file content inside a panel
- Widget-ize subprocesses with scrolling output
- Progress bars! PROGRESS BARS!
- Provide means to encapsulate whole canvasses, drawing widgets on top and eliminating the need to manually wrap curses
- Improve panel handling, provide interface for moving panels
- A better menu system that doesn't require class instantiation to chain widgets together (maybe solvable by a larger abstraction?)

## Classes
### Menu
---
- Constructor: Menu(title, subtitle, items, stdscr)
  - title: String for title of menu, bold
  - subtitle: String for subtitle of menu, underlined
  - item: list, or other iterable, with iterable entries as follows:
    - ('Entry text', wrappable action, Boolean value indicating whether to break the menu)
      - Boolean menu break allows you to customize your own "Continue"
      - Set entry action to `exit` to force a hard quit, if you like
  - stdscr: A curses-initialized window object on which to build the menu
- show method:
  - Initiates menu display immediately
  - Returns nothing

Arrow keys or index numbers can be used to navigate the menu. Enter selects, performing the action.

### InputBox
---
- Constructor: InputBox(title, default, length, stdscr)
  - title: String for the title on the box
  - default: String for the default value to fill the input box
  - length: Integer representing width of space to allow input
  - stdscr: Parent curses window on which to draw subwindow/panel
- show method:
  - Spawns InputBox panel on parent stdscr, allows editing until Enter pressed
  - Returns value
- value property:
  - Stores default value until show is called, stores modified value after
- title property:
  - Stores title used to instantiate the InputBox, so you can create a hash table of questions and answers if you like

### MessageBox
---
- Constructor: MessageBox(title, message, stdscr)
  - title: String for the title on the box
  - message: String for the message to display
  - stdscr: Parent curses window on which to draw subwindow/panel
- show method:
  - Spawns simple message box panel with OK button
  - Returns nothing
- title property:
  - Stores title used to instantiate MessageBox
- message property:
  - Stores message used to instantiate MessageBox as a list, split on newlines

### YesNoBox
---
- Constructor: YesNoBox(title, message, stdscr)
  - title: String for the title on the  box
  - message: String for the message to display
  - stdscr: Parent curses window on which to draw subwindow/panel
- show method:
  - Spawns message box with YES/NO buttons
    - pressing Y or N quick-selects an option
    - Arrow keys move between options
    - Enter selects highlighted option
  - Returns True if YES, False if NO
- title property:
  - Stores title used to instantiate YesNoBox
- message property:
  - Stores message used to instantiate YesNoBox as a list, split on newlines
