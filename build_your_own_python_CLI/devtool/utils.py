from rich.console import Console
from rich.table import Table

console = Console()

def display_notes(notes):
    """Prints a list of notes in a beautiful, formatted table."""
    if not notes:
        console.print("[bold yellow]📭 No notes found. Add one using 'devtool add'![/bold yellow]")
        return

    table = Table(title="📝 Your Notes", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="green", no_wrap=True)
    table.add_column("Content", style="white")
    table.add_column("Created At", style="dim")

    for note in notes:
        # Handle cases where content might be None
        content_preview = note["content"] if note["content"] else ""
        if len(content_preview) > 40:
            content_preview = content_preview[:40] + "..."
            
        table.add_row(
            str(note["id"]), 
            note["title"], 
            content_preview, 
            note["created_at"]
        )
    
    console.print(table)