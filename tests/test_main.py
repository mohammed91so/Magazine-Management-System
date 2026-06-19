"""
Unit tests for main application navigation behavior.
"""

from main import App


class DummyPage:
    """Simple page double for navigation tests."""

    def __init__(self, events, with_on_show=True):
        self.events = events
        if with_on_show:
            self.on_show = self._on_show

    def _on_show(self):
        self.events.append("on_show")

    def tkraise(self):
        self.events.append("tkraise")


class DummyApp:
    """Simple app double exposing only the pages mapping."""

    def __init__(self, pages):
        self.pages = pages


class TestAppNavigation:
    """Test navigation lifecycle behavior."""

    def test_show_page_calls_on_show_before_tkraise(self, monkeypatch):
        events = []
        page = DummyPage(events)
        app = DummyApp({"dashboard": page})
        operations = []

        monkeypatch.setattr("main.monitoring.log_operation", operations.append)

        App.show_page(app, "dashboard")

        assert events == ["on_show", "tkraise"]
        assert operations == ["page_switch_dashboard"]

    def test_show_page_still_raises_page_without_on_show(self, monkeypatch):
        events = []
        page = DummyPage(events, with_on_show=False)
        app = DummyApp({"reports": page})
        operations = []

        monkeypatch.setattr("main.monitoring.log_operation", operations.append)

        App.show_page(app, "reports")

        assert events == ["tkraise"]
        assert operations == ["page_switch_reports"]

    def test_refresh_all_pages_calls_on_show_when_available(self):
        events = []
        dashboard = DummyPage(events)
        reports = DummyPage(events, with_on_show=False)
        sales = DummyPage(events)
        app = DummyApp({"dashboard": dashboard, "reports": reports, "sales": sales})

        App.refresh_all_pages(app)

        assert events == ["on_show", "on_show"]
