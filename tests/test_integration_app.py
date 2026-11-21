"""Integration tests: OrderService + ProductRepository + calculation functions."""


class TestIntegrationOrderService:
    def test_integration_successful_order(self, order_service):
        result = order_service.place_order("SHIRT", 2)

        assert result["success"] is True
        assert result["item"] == "T-Shirt"
        assert result["quantity"] == 2
        assert result["total"] == 60.0  # 2 * 25 = 50, + 20 % = 60

    def test_integration_stock_is_reduced_after_order(self, order_service):
        order_service.place_order("MUG", 3)
        assert order_service.repo.get_product("MUG")["stock"] == 97

    def test_integration_order_unknown_product(self, order_service):
        result = order_service.place_order("PANTS", 1)
        assert result == {"success": False, "error": "Product not found"}

    def test_integration_order_exceeds_stock(self, order_service):
        result = order_service.place_order("HAT", 999)
        assert result == {"success": False, "error": "Not enough stock"}

    def test_integration_failed_order_does_not_touch_stock(self, order_service):
        order_service.place_order("HAT", 999)
        assert order_service.repo.get_product("HAT")["stock"] == 30

    def test_integration_multiple_orders_deplete_stock(self, order_service):
        order_service.place_order("HAT", 10)
        order_service.place_order("HAT", 15)
        assert order_service.repo.get_product("HAT")["stock"] == 5

    def test_integration_exact_stock_can_be_bought(self, order_service):
        result = order_service.place_order("HAT", 30)
        assert result["success"] is True
        assert order_service.place_order("HAT", 1)["error"] == "Not enough stock"
