from typer.testing import CliRunner
from devtool.cli import app
import os
import pytest
import tempfile

# Initialize the test runner
runner = CliRunner()

@pytest.fixture(autouse=True)
def use_temp_database(monkeypatch):
    """
    Creates a temporary database file for each test.
    This prevents Windows 'PermissionError' by ensuring tests
    never touch the real database in your home folder.
    """
    # Create a temporary directory and a fake db path inside it
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_devtool.db")
    
    # We use monkeypatch to force the database module to use our temp path
    from devtool import database
    monkeypatch.setattr(database, "DB_PATH", temp_db_path)
    monkeypatch.setattr(database, "APP_DIR", temp_dir)
    
    yield
    
    # Cleanup (optional, the OS will clean up the temp folder eventually)
    try:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        os.rmdir(temp_dir)
    except Exception:
        pass


def test_help_command():
    """Test that the help menu works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "devtool" in result.stdout


def test_add_and_list():
    """Test adding a note and then listing it."""
    # 1. Test adding
    result_add = runner.invoke(app, ["add", "Test Title", "-c", "Test Content"])
    assert result_add.exit_code == 0
    assert "Note added with ID 1" in result_add.stdout

    # 2. Test listing
    result_list = runner.invoke(app, ["list"])
    assert result_list.exit_code == 0
    assert "Test Title" in result_list.stdout
    assert "Test Content" in result_list.stdout


def test_delete_note():
    """Test adding a note and deleting it."""
    # Add a note
    runner.invoke(app, ["add", "To Be Deleted"])
    
    # Delete it (simulating the user typing 'y' for confirm)
    result = runner.invoke(app, ["delete", "1"], input="y\n")
    assert result.exit_code == 0
    assert "deleted successfully" in result.stdout
    
    # Verify it's gone
    result_list = runner.invoke(app, ["list"])
    assert "To Be Deleted" not in result_list.stdout