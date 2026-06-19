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


class DummyButton:
    """Simple button double for navigation-state tests."""

    def __init__(self):
        self.configure_calls = []

    def configure(self, **kwargs):
        self.configure_calls.append(kwargs)


class DummyApp:
    """Simple app double exposing only the pages mapping."""

    ACTIVE_NAV_FG_COLOR = App.ACTIVE_NAV_FG_COLOR
    ACTIVE_NAV_HOVER_COLOR = App.ACTIVE_NAV_HOVER_COLOR

    def __init__(self, pages, nav_buttons=None):
        self.pages = pages
        self.nav_buttons = nav_buttons or {}
        self.nav_button_defaults = {
            name: {"fg_color": "default-fg", "hover_color": "default-hover"}
            for name in self.nav_buttons
        }
        self.current_page = None

    def update_navigation_state(self, active_page):
        App.update_navigation_state(self, active_page)


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
        button = DummyButton()
        app = DummyApp({"reports": page}, {"reports": button})
        operations = []

        monkeypatch.setattr("main.monitoring.log_operation", operations.append)

        App.show_page(app, "reports")

        assert events == ["tkraise"]
        assert operations == ["page_switch_reports"]
        assert app.current_page == "reports"
        assert button.configure_calls[-1] == {
            "fg_color": App.ACTIVE_NAV_FG_COLOR,
            "hover_color": App.ACTIVE_NAV_HOVER_COLOR,
        }

    def test_refresh_all_pages_calls_on_show_when_available(self):
        events = []
        dashboard = DummyPage(events)
        reports = DummyPage(events, with_on_show=False)
        sales = DummyPage(events)
        app = DummyApp({"dashboard": dashboard, "reports": reports, "sales": sales})

        App.refresh_all_pages(app)

        assert events == ["on_show", "on_show"]

    def test_update_navigation_state_marks_only_selected_button_active(self):
        dashboard_button = DummyButton()
        products_button = DummyButton()
        reports_button = DummyButton()
        app = DummyApp(
            pages={},
            nav_buttons={
                "dashboard": dashboard_button,
                "products": products_button,
                "reports": reports_button,
            },
        )

        App.update_navigation_state(app, "products")

        assert app.current_page == "products"
        assert products_button.configure_calls[-1] == {
            "fg_color": App.ACTIVE_NAV_FG_COLOR,
            "hover_color": App.ACTIVE_NAV_HOVER_COLOR,
        }
        assert dashboard_button.configure_calls[-1] == {
            "fg_color": "default-fg",
            "hover_color": "default-hover",
        }
        assert reports_button.configure_calls[-1] == {
            "fg_color": "default-fg",
            "hover_color": "default-hover",
        }

    def test_show_page_updates_navigation_state_after_successful_switch(self, monkeypatch):
        events = []
        page = DummyPage(events)
        dashboard_button = DummyButton()
        products_button = DummyButton()
        app = DummyApp(
            {"products": page},
            {"dashboard": dashboard_button, "products": products_button}
        )
        operations = []

        monkeypatch.setattr("main.monitoring.log_operation", operations.append)

        App.show_page(app, "products")

        assert events == ["on_show", "tkraise"]
        assert app.current_page == "products"
        assert products_button.configure_calls[-1] == {
            "fg_color": App.ACTIVE_NAV_FG_COLOR,
            "hover_color": App.ACTIVE_NAV_HOVER_COLOR,
        }
        assert dashboard_button.configure_calls[-1] == {
            "fg_color": "default-fg",
            "hover_color": "default-hover",
        }
        assert operations == ["page_switch_products"]

    def test_show_page_does_not_change_navigation_state_for_unknown_page(self, monkeypatch):
        button = DummyButton()
        app = DummyApp({"dashboard": DummyPage([])}, {"dashboard": button})
        operations = []

        monkeypatch.setattr("main.monitoring.log_operation", operations.append)

        App.show_page(app, "missing")

        assert app.current_page is None
        assert button.configure_calls == []
        assert operations == []
