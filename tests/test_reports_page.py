"""
Unit tests for Reports page backup management helpers.
"""

from pathlib import Path

from config.settings import settings
from ui.reports import ReportsPage


class DummyReportsPage:
    """Minimal page double for testing ReportsPage helper methods."""

    def __init__(self, selected_backup_path=None, available_backups=None):
        self.selected_backup_path = selected_backup_path
        self.available_backups = available_backups or []
        self.load_calls = 0

    def _format_size(self, size_bytes):
        return ReportsPage._format_size(self, size_bytes)

    def _is_within_backup_dir(self, selected_path, backup_dir):
        return ReportsPage._is_within_backup_dir(self, selected_path, backup_dir)

    def _validate_selected_backup(self, backup_path):
        return ReportsPage._validate_selected_backup(self, backup_path)

    def _load_backups(self):
        self.load_calls += 1


class DummyApp:
    """Minimal app double for restore coordination tests."""

    def __init__(self, refresh_raises=False):
        self.refresh_calls = 0
        self.refresh_raises = refresh_raises

    def refresh_all_pages(self):
        self.refresh_calls += 1
        if self.refresh_raises:
            raise RuntimeError("refresh failed")


class DummyRestorePage(DummyReportsPage):
    """Reports page double with restore workflow hooks."""

    def __init__(self, selected_backup_path=None, app=None):
        super().__init__(selected_backup_path=selected_backup_path)
        self.app = app or DummyApp()
        self.refresh_backups_calls = 0

    def refresh_backups(self):
        self.refresh_backups_calls += 1

    def winfo_toplevel(self):
        return self.app


class TestReportsPageHelpers:
    """Test ReportsPage backup helper behavior."""

    def test_validate_selected_backup_accepts_valid_file_inside_backup_dir(self, tmp_path, monkeypatch):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        backup_file = backup_dir / "inventory_20260101_120000.db"
        backup_file.write_text("backup")
        page = DummyReportsPage()

        monkeypatch.setattr(settings, "BACKUP_PATH", backup_dir)

        result = ReportsPage._validate_selected_backup(page, backup_file)

        assert result == backup_file.resolve()

    def test_validate_selected_backup_rejects_missing_file(self, tmp_path, monkeypatch):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        missing_file = backup_dir / "missing.db"
        page = DummyReportsPage()

        monkeypatch.setattr(settings, "BACKUP_PATH", backup_dir)

        try:
            ReportsPage._validate_selected_backup(page, missing_file)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert str(e) == "Selected backup file does not exist"

    def test_validate_selected_backup_rejects_directory(self, tmp_path, monkeypatch):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        page = DummyReportsPage()

        monkeypatch.setattr(settings, "BACKUP_PATH", backup_dir)

        try:
            ReportsPage._validate_selected_backup(page, backup_dir)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert str(e) == "Selected backup path is not a file"

    def test_validate_selected_backup_rejects_file_outside_backup_dir(self, tmp_path, monkeypatch):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        outside_file = tmp_path / "elsewhere.db"
        outside_file.write_text("backup")
        page = DummyReportsPage()

        monkeypatch.setattr(settings, "BACKUP_PATH", backup_dir)

        try:
            ReportsPage._validate_selected_backup(page, outside_file)
            assert False, "Expected ValueError"
        except ValueError as e:
            assert str(e) == "Selected backup must be inside the configured backup directory"

    def test_build_backup_display_item_includes_timestamp_and_size(self, tmp_path):
        backup_file = tmp_path / "inventory_20260101_120000.db"
        backup_file.write_bytes(b"x" * 2048)
        page = DummyReportsPage()

        item = ReportsPage._build_backup_display_item(page, backup_file)

        assert item["path"] == backup_file
        assert "KB" in item["size"]
        assert item["label"]


class TestReportsPageRestoreWorkflow:
    """Test restore workflow coordination."""

    def test_restore_is_blocked_when_no_backup_is_selected(self, monkeypatch):
        page = DummyRestorePage(selected_backup_path=None)
        warnings = []

        monkeypatch.setattr("ui.reports.messagebox.showwarning", lambda title, msg: warnings.append((title, msg)))

        ReportsPage.restore_selected_backup(page)

        assert warnings == [("Restore Blocked", "Please select a backup to restore")]

    def test_restore_calls_restore_backup_after_validation(self, tmp_path, monkeypatch):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        backup_file = backup_dir / "inventory_20260101_120000.db"
        backup_file.write_text("backup")
        page = DummyRestorePage(selected_backup_path=backup_file)
        restore_calls = []
        infos = []

        monkeypatch.setattr(settings, "BACKUP_PATH", backup_dir)
        monkeypatch.setattr("ui.reports.restore_backup", lambda path: restore_calls.append(path))
        monkeypatch.setattr("ui.reports.messagebox.askyesno", lambda *args, **kwargs: True)
        monkeypatch.setattr("ui.reports.messagebox.showinfo", lambda title, msg: infos.append((title, msg)))
        monkeypatch.setattr("ui.reports.messagebox.showwarning", lambda *args, **kwargs: None)

        ReportsPage.restore_selected_backup(page)

        assert restore_calls == [backup_file.resolve()]
        assert page.app.refresh_calls == 1
        assert page.refresh_backups_calls == 1
        assert infos and infos[0][0] == "Restore Completed"

    def test_restore_shows_restart_warning_if_refresh_fails(self, tmp_path, monkeypatch):
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()
        backup_file = backup_dir / "inventory_20260101_120000.db"
        backup_file.write_text("backup")
        page = DummyRestorePage(selected_backup_path=backup_file, app=DummyApp(refresh_raises=True))
        warnings = []

        monkeypatch.setattr(settings, "BACKUP_PATH", backup_dir)
        monkeypatch.setattr("ui.reports.restore_backup", lambda path: None)
        monkeypatch.setattr("ui.reports.messagebox.askyesno", lambda *args, **kwargs: True)
        monkeypatch.setattr("ui.reports.messagebox.showwarning", lambda title, msg: warnings.append((title, msg)))
        monkeypatch.setattr("ui.reports.messagebox.showinfo", lambda *args, **kwargs: None)

        ReportsPage.restore_selected_backup(page)

        assert page.app.refresh_calls == 1
        assert page.refresh_backups_calls == 1
        assert warnings
        assert warnings[0][0] == "Restore Completed"
        assert "Please restart the application" in warnings[0][1]
