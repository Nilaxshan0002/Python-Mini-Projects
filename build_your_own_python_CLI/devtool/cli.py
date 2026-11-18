import typer
from rich import print
from rich.prompt import Confirm
from devtool.database import get_connection, init_db
from devtool.utils import display_notes

# Initialize the Typer app
app = typer.Typer(
    help="🛠️ devtool: A custom Python CLI for developers to manage quick notes.",
    no_args_is_help=True
)

@app.callback()
def main():
    """
    devtool: Developer utility CLI.
    This callback runs before any command to ensure the database exists.
    """
    init_db()

@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the note"),
    content: str = typer.Option(None, "--content", "-c", help="Detailed content of the note")
):
    """
    Add a new note to the database.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)", 
            (title, content)
        )
        conn.commit()
        note_id = cursor.lastrowid
        
    print(f"✅ [bold green]Success![/bold green] Note added with ID [cyan]{note_id}[/cyan].")

@app.command("list")
def list_notes():
    """
    List all saved notes.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes ORDER BY id DESC")
        notes = cursor.fetchall()
    
    display_notes(notes)

@app.command()
def delete(
    note_id: int = typer.Argument(..., help="The ID of the note to delete")
):
    """
    Delete a note by its ID.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # First, check if the note exists
        cursor.execute("SELECT title FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        
        if not note:
            print(f"❌ [bold red]Error:[/bold red] Note with ID {note_id} not found.")
            raise typer.Exit(code=1)
            
        # Ask for confirmation before deleting
        confirm = Confirm.ask(f"Are you sure you want to delete '[yellow]{note['title']}[/yellow]'?")
        
        if confirm:
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            print(f"🗑️ [bold yellow]Note {note_id} deleted successfully.[/bold yellow]")
        else:
            print("❌ Deletion cancelled.")

if __name__ == "__main__":
    app()