# Nudge - Spaced Repetition Study Reminder

A lightweight desktop application for macOS that helps you remember what you study by using the forgetting curve to schedule reviews.

## Features

- **Spaced Repetition**: Automatically schedules reviews based on the forgetting curve (1, 3, 7, 14, 30, 60, 120 days)
- **Custom Tags**: Organize your study items with color-coded tags
- **System Tray Integration**: Runs in the background with easy access from the menu bar
- **Simple UI**: Clean interface to manage items and track upcoming reviews
- **Local Storage**: All data stored locally in SQLite - no internet required

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Setup

1. Navigate to the project directory:
```bash
cd nudge
```

2. Install dependencies:
```bash
poetry install
```

3. Run the application:
```bash
poetry run python -m nudge
```

Or use the Poetry script:
```bash
poetry run nudge
```

## Usage

### Adding Items

1. Click the "Add Item" button in the main window
2. Enter the item name (e.g., "Python decorators", "French vocabulary")
3. Add one or more tags to categorize the item
4. Click OK

Tags are automatically assigned random colors. You can create new tags by typing them in.

### Viewing Items

The main window shows all your study items with:
- **Name**: What you're studying
- **Tags**: Categories for organization
- **Date Added**: When you first added it
- **Next Review**: When you should review it next
- **Interval**: Current review interval

Items due today are highlighted in light red, and items due soon are highlighted in light yellow.

### Marking Items as Reviewed

1. Select an item in the table
2. Click "Mark as Reviewed"
3. The item advances to the next interval automatically

The intervals progress through: 1 day → 3 days → 7 days → 14 days → 30 days → 60 days → 120 days

After reaching 120 days, items are marked as "mastered" and continue at 120-day intervals.

### Deleting Items

1. Select an item in the table
2. Click "Delete Item"
3. Confirm the deletion

**Note**: Deletion is permanent and cannot be undone.

### System Tray

The application runs in the system tray (menu bar on macOS):
- **Double-click** the tray icon to show/hide the main window
- **Right-click** for menu options:
  - Show Window
  - Quick Add Item
  - Quit

### Search and Filter

Use the search box at the top to filter items by name or tag.

## Data Storage

All data is stored locally in:
```
~/Library/Application Support/Nudge/nudge.db
```

This SQLite database contains:
- Your study items
- Tags with colors
- Review schedules and history

## Project Structure

```
nudge/
├── nudge/
│   ├── core/           # Database models and business logic
│   │   ├── database.py
│   │   ├── models.py
│   │   └── scheduler.py
│   ├── ui/             # User interface components
│   │   ├── windows/
│   │   ├── dialogs/
│   │   └── widgets/
│   ├── services/       # Background services
│   │   └── tray_service.py
│   ├── app.py          # Application initialization
│   └── __main__.py     # Entry point
├── tests/
├── pyproject.toml
└── README.md
```

## Troubleshooting

### Application won't start

Make sure all dependencies are installed:
```bash
poetry install
```

### Can't see the system tray icon

On macOS, check your menu bar. The icon should appear on the right side near the clock.

### Database issues

If you encounter database errors, you can reset the database by deleting:
```bash
rm ~/Library/Application\ Support/Nudge/nudge.db
```

The application will create a new database on next launch.
