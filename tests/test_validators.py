"""
Unit tests for validation utilities.
"""

import pytest
from utils.validators import (
    validate_product_name,
    validate_price,
    validate_quantity,
    validate_expiration_date,
    validate_product_id,
    ValidationError
)


class TestValidateProductName:
    """Test product name validation."""
    
    def test_valid_name(self):
        assert validate_product_name("Canned Beans") == "Canned Beans"
        assert validate_product_name("  Canned Beans  ") == "Canned Beans"
    
    def test_empty_name(self):
        with pytest.raises(ValidationError, match="Product name is required"):
            validate_product_name("")
        with pytest.raises(ValidationError, match="Product name is required"):
            validate_product_name("   ")
    
    def test_short_name(self):
        with pytest.raises(ValidationError, match="at least 2 characters"):
            validate_product_name("A")
    
    def test_long_name(self):
        with pytest.raises(ValidationError, match="not exceed 100 characters"):
            validate_product_name("A" * 101)


class TestValidatePrice:
    """Test price validation."""
    
    def test_valid_price(self):
        assert validate_price(10.50) == 10.50
        assert validate_price("10.50") == 10.50
        assert validate_price(0) == 0.0
    
    def test_negative_price(self):
        with pytest.raises(ValidationError, match="cannot be negative"):
            validate_price(-10.50)
    
    def test_invalid_price(self):
        with pytest.raises(ValidationError, match="must be a valid number"):
            validate_price("invalid")
        with pytest.raises(ValidationError, match="must be a valid number"):
            validate_price(None)
    
    def test_unreasonably_high_price(self):
        with pytest.raises(ValidationError, match="unreasonably high"):
            validate_price(1000001)


class TestValidateQuantity:
    """Test quantity validation."""
    
    def test_valid_quantity(self):
        assert validate_quantity(50) == 50
        assert validate_quantity("50") == 50
        assert validate_quantity(0) == 0
    
    def test_negative_quantity(self):
        with pytest.raises(ValidationError, match="cannot be negative"):
            validate_quantity(-10)
    
    def test_invalid_quantity(self):
        with pytest.raises(ValidationError, match="must be a valid integer"):
            validate_quantity("invalid")
        # Float is now accepted and converted to int
    
    def test_unreasonably_high_quantity(self):
        with pytest.raises(ValidationError, match="unreasonably high"):
            validate_quantity(100001)


class TestValidateExpirationDate:
    """Test expiration date validation."""
    
    def test_valid_date(self):
        assert validate_expiration_date("2025-12-31") == "2025-12-31"
        assert validate_expiration_date("  2025-12-31  ") == "2025-12-31"
    
    def test_empty_date(self):
        with pytest.raises(ValidationError, match="Expiration date is required"):
            validate_expiration_date("")
        with pytest.raises(ValidationError, match="Expiration date is required"):
            validate_expiration_date("   ")
    
    def test_invalid_format(self):
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_expiration_date("12/31/2025")
        with pytest.raises(ValidationError, match="Invalid date format"):
            validate_expiration_date("2025-31-12")
    
    def test_old_date(self):
        with pytest.raises(ValidationError, match="cannot be before year 2000"):
            validate_expiration_date("1999-12-31")


class TestValidateProductId:
    """Test product ID validation."""
    
    def test_valid_id(self):
        assert validate_product_id(1) == 1
        assert validate_product_id("1") == 1
    
    def test_negative_id(self):
        with pytest.raises(ValidationError, match="must be positive"):
            validate_product_id(-1)
        with pytest.raises(ValidationError, match="must be positive"):
            validate_product_id(0)
    
    def test_invalid_id(self):
        with pytest.raises(ValidationError, match="must be a valid integer"):
            validate_product_id("invalid")
        with pytest.raises(ValidationError, match="must be a valid integer"):
            validate_product_id(None)
