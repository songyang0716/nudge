"""Main entry point for the Nudge application."""
import sys

from nudge.app import NudgeApp


def main():
    """Main entry point."""
    app = NudgeApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
