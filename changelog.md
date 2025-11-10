# Update f-10nov2025

### General Updates

-   **Updated dependencies**
-   **Created** `requirements.txt`: (as an alternative)
-   **Edited** `README.md`: to make it prettier and more _functional_ in my opinion.
-   **Edited** `CONTRIBUTING.md`: a quick message for this repository and the original creators.
-   **Edited** `SECURITY.md`: to reflect upon this repository system.
-   **Added** everything above

### 1.TabWidget Class (qt.py)

-   TABS ARE HERE!!!!
-   Automatic tab title updates based on page titles
-   The url and actions like url/search + control buttons now apply to the currently opened tab
-   "`+`" button for creating new tabs
-   Prevents closing the last tab (navigates to homepage instead)
-   Made log notes, like `[Fatal]`; `[Err]`; `[Warn]`

### 2. Better Main Window (window.py)

-   Replaced single web view with tabbed interface
-   Updated all navigation buttons to work with active tab
-   Added new tab button in navigation bar
-   Proper URL synchronization with active tab

### 3. Keyboard Shortcuts

-   `Ctrl+T` - New tab
-   `Ctrl+W` - Close current tab
-   `Ctrl+Tab` - Next tab
-   `Ctrl+Shift+Tab` - Previous tab
-   `F5 or Ctrl+R` - Refresh current tab
-   `Ctrl+L` - Focus address bar and select all
