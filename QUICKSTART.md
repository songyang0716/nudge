# Nudge - Quick Start Guide

## What is Nudge?

Nudge is a spaced repetition study reminder that helps you remember what you learn by scheduling reviews based on the scientifically-proven forgetting curve.

## Key Concepts

### Spaced Repetition
Instead of cramming, you review material at increasing intervals:
- **Day 1**: Initial review
- **Day 3**: First follow-up (2 days later)
- **Day 7**: Second follow-up (4 days later)
- **Day 14**: Third follow-up (7 days later)
- **Day 30**: Fourth follow-up (16 days later)
- **Day 60**: Fifth follow-up (30 days later)
- **Day 120**: Sixth follow-up (60 days later)

After 120 days, items are marked as "mastered" and continue at 120-day intervals.

### How It Works

1. **Add an item** - Anything you want to remember (a concept, vocabulary, formula, etc.)
2. **Tag it** - Organize by subject (Python, French, Math, etc.)
3. **Check daily** - Open Nudge to see what's due for review
4. **Mark as reviewed** - After reviewing the material, mark it as reviewed
5. **Item advances** - The item automatically moves to the next interval

## Your First Study Session

### 1. Add Your First Item

Today (January 25, 2026), you decide to study Python decorators:

1. Click **"Add Item"**
2. Enter name: "Python decorators"
3. Add tags: "Python", "Programming"
4. Click **OK**

The item is scheduled for first review on **January 26, 2026** (1 day).

### 2. Review Tomorrow

Open Nudge on January 26. You'll see:
- **Python decorators** is highlighted (due today)

Review the material, then:
1. Select the item
2. Click **"Mark as Reviewed"**

Now it's scheduled for **January 29, 2026** (3 days later).

### 3. Keep Going

- **Jan 29**: Review again → Next review **Feb 5** (7 days)
- **Feb 5**: Review again → Next review **Feb 19** (14 days)
- **Feb 19**: Review again → Next review **Mar 21** (30 days)
- And so on...

## Tips for Success

### Daily Habit
- Open Nudge every day to check what's due
- The main window highlights overdue items in red
- Items due today are highlighted in yellow

### Tagging Strategy
- Use tags to group related items
- Common tags: subject name, difficulty level, course name
- Tags help you filter and search

### What to Add
Good candidates for spaced repetition:
- **Vocabulary** (foreign languages)
- **Concepts** (programming patterns, theories)
- **Formulas** (math, physics, chemistry)
- **Facts** (historical dates, definitions)
- **Procedures** (algorithms, processes)

### When to Delete
Delete items when:
- You've truly mastered them (after many successful reviews)
- The information is no longer relevant
- You made a mistake entering it

## System Tray Usage

Since Nudge runs in the background:

1. **Double-click** the tray icon to open the main window
2. **Right-click** for quick actions:
   - Quick Add: Add an item without opening the main window
   - Show Window: Open the main window
   - Quit: Close the application

## Example Workflow

Let's say you're learning French and programming:

### Monday (Study Session)
Add these items:
- "French: avoir conjugation" (Tag: French)
- "French: être conjugation" (Tag: French)
- "Python: list comprehensions" (Tag: Python)
- "Python: generators" (Tag: Python)

### Tuesday
Open Nudge:
- All 4 items show as due today (red highlight)
- Review each one and mark as reviewed
- They're now scheduled for Friday (3 days)

### Friday
Open Nudge:
- All 4 items due again
- Review and mark as reviewed
- Next review: Next Friday (7 days)

### The Following Week
Continue this pattern. As items prove easier to remember, they naturally space out to longer intervals.

## Searching and Filtering

Use the search box to find items:
- Search by name: "avoir"
- Search by tag: "French"
- Results update as you type

## Managing Your Data

### View All Items
The main table shows:
- Item name
- Associated tags (color-coded)
- Date you added it
- Next review date
- Current interval stage

### Sort Items
Click column headers to sort (feature to be added)

### Data Location
Your data is stored at:
```
~/Library/Application Support/Nudge/nudge.db
```

This is a local SQLite database - no cloud, no internet required.

## Common Questions

**Q: What if I miss a review day?**
A: No problem! The item will show as overdue (red). Just review it when you can and mark as reviewed. The next interval starts from that date.

**Q: Can I review an item early?**
A: Yes, but it's not recommended. The intervals are scientifically designed. Reviewing too early defeats the purpose.

**Q: What if I get something wrong during review?**
A: Currently, you can delete and re-add the item to restart from day 1. Future versions may include a "reset" feature.

**Q: How many items should I add?**
A: Start small (5-10 items). Add more as you get comfortable with the daily review habit.

**Q: Can I change the intervals?**
A: Not currently. The intervals (1, 3, 7, 14, 30, 60, 120 days) are based on research into optimal retention.

## Running the App

Start Nudge with:
```bash
poetry run nudge
```

The app will:
1. Create the database if it doesn't exist
2. Show the main window
3. Add a system tray icon
4. Stay running in the background

To quit, right-click the tray icon and select "Quit".

---

Happy studying! 🎓
