from .server import mcp


def main() -> None:
    """
    Entry point for the CLI script.
    """
    mcp.run()


if __name__ == "__main__":
    main()
