"""
Unit tests for Products page filtering helpers.
"""

from ui.products import ProductsPage


class DummySearchVar:
    """Simple replacement for StringVar in helper-level tests."""

    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value


class DummyProductsPage:
    """Minimal page double for testing ProductsPage helper methods."""

    def __init__(self, selected_filter="All", search_text=""):
        self.selected_filter = selected_filter
        self.search_var = DummySearchVar(search_text)


class TestProductsPageFiltering:
    """Test ProductsPage helper methods without a real GUI."""

    def test_get_products_for_filter_all(self, monkeypatch):
        expected = [{"name": "All Product"}]
        page = DummyProductsPage()

        monkeypatch.setattr("ui.products.list_products", lambda: expected)

        result = ProductsPage._get_products_for_filter(page, "All")

        assert result == expected

    def test_get_products_for_filter_low_stock_uses_threshold_ten(self, monkeypatch):
        calls = []
        expected = [{"name": "Low Stock"}]
        page = DummyProductsPage()

        def fake_get_low_stock_products(threshold):
            calls.append(threshold)
            return expected

        monkeypatch.setattr("ui.products.get_low_stock_products", fake_get_low_stock_products)

        result = ProductsPage._get_products_for_filter(page, "Low stock")

        assert result == expected
        assert calls == [10]

    def test_get_products_for_filter_out_of_stock(self, monkeypatch):
        expected = [{"name": "Out"}]
        page = DummyProductsPage()

        monkeypatch.setattr("ui.products.get_out_of_stock_products", lambda: expected)

        result = ProductsPage._get_products_for_filter(page, "Out of stock")

        assert result == expected

    def test_get_products_for_filter_expired(self, monkeypatch):
        expected = [{"name": "Expired"}]
        page = DummyProductsPage()

        monkeypatch.setattr("ui.products.get_expired_products", lambda: expected)

        result = ProductsPage._get_products_for_filter(page, "Expired")

        assert result == expected

    def test_get_products_for_filter_expiring_soon(self, monkeypatch):
        expected = [{"name": "Soon"}]
        page = DummyProductsPage()

        monkeypatch.setattr("ui.products.get_expiring_soon_products", lambda: expected)

        result = ProductsPage._get_products_for_filter(page, "Expiring soon")

        assert result == expected

    def test_apply_search_is_case_insensitive(self):
        page = DummyProductsPage()
        products = [
            {"name": "Canned Beans"},
            {"name": "Tomato Soup"},
        ]

        result = ProductsPage._apply_search(page, products, "beans")

        assert result == [{"name": "Canned Beans"}]

    def test_apply_search_trims_whitespace(self):
        page = DummyProductsPage()
        products = [
            {"name": "Canned Beans"},
            {"name": "Tomato Soup"},
        ]

        result = ProductsPage._apply_search(page, products, "  soup  ")

        assert result == [{"name": "Tomato Soup"}]

    def test_apply_search_with_empty_text_returns_original_list(self):
        page = DummyProductsPage()
        products = [{"name": "Canned Beans"}]

        result = ProductsPage._apply_search(page, products, "   ")

        assert result is products

    def test_get_filtered_products_combines_filter_and_search(self, monkeypatch):
        page = DummyProductsPage(selected_filter="Low stock", search_text="corn")
        low_stock_products = [
            {"name": "Canned Corn"},
            {"name": "Canned Beans"},
        ]

        monkeypatch.setattr(page, "_get_products_for_filter", lambda filter_name: low_stock_products, raising=False)
        monkeypatch.setattr(page, "_apply_search", lambda products, search_text: [
            product for product in products if search_text in product["name"].lower()
        ], raising=False)

        result = ProductsPage._get_filtered_products(page)

        assert result == [{"name": "Canned Corn"}]

    def test_refresh_renders_from_stored_state_without_resetting_it(self, monkeypatch):
        page = DummyProductsPage(selected_filter="Expired", search_text="milk")
        calls = {}

        monkeypatch.setattr(page, "_get_filtered_products", lambda: [{"name": "Expired Milk"}], raising=False)
        monkeypatch.setattr(
            page,
            "_render_products",
            lambda products: calls.setdefault("products", products),
            raising=False
        )

        ProductsPage.refresh(page)

        assert calls["products"] == [{"name": "Expired Milk"}]
        assert page.selected_filter == "Expired"
        assert page.search_var.get() == "milk"
