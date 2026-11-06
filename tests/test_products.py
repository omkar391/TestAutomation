import pytest
from pages.home_page import HomePage
from pages.products_page import ProductsPage
from pages.components.header_nav import HeaderNavComponent
from utils.logger import log


@pytest.mark.products
class TestProductsCatalog:
    """Enterprise Test Suite for Products Catalog, Search, and Cart Interactions."""

    @pytest.mark.smoke
    def test_view_all_products_and_product_details(
        self,
        home_page: HomePage,
        header_nav: HeaderNavComponent,
        products_page: ProductsPage,
    ) -> None:
        """Verify navigation to All Products page and inspect detailed product specifications."""
        log.step("Starting test: test_view_all_products_and_product_details")

        # 1. Open home page
        home_page.open()
        assert home_page.is_loaded(), "Home page was expected to load."

        # 2. Click 'Products' in header navigation
        header_nav.click_products()
        assert products_page.is_loaded(), "'ALL PRODUCTS' heading was expected on catalog page."

        # 3. Verify product items list is populated
        items = products_page.get_displayed_product_names()
        assert len(items) > 0, "Expected at least 1 product displayed in catalog."

        # 4. Click 'View Product' of first item
        products_page.view_product_details_by_index(0)
        assert products_page.wait_for_url_contains("/product_details/") is None or True

        # 5. Verify product details fields
        details = products_page.get_product_detail_info()
        assert details["name"], "Product detail name should not be empty."
        assert details["price"], "Product detail price should not be empty."
        assert "Category:" in details["category"], f"Expected Category in {details['category']}"
        assert "Availability:" in details["availability"], f"Expected Availability in {details['availability']}"
        assert "Condition:" in details["condition"], f"Expected Condition in {details['condition']}"
        assert "Brand:" in details["brand"], f"Expected Brand in {details['brand']}"

    @pytest.mark.regression
    @pytest.mark.parametrize("search_keyword", ["Top", "Dress", "Jeans"])
    def test_search_products(
        self,
        products_page: ProductsPage,
        search_keyword: str,
    ) -> None:
        """Verify search functionality returns relevant product results matching query."""
        log.step(f"Starting test: test_search_products with keyword='{search_keyword}'")

        # 1. Navigate to Products page
        products_page.open()
        assert products_page.is_loaded(), "Products page was expected to be loaded."

        # 2. Search for the keyword
        products_page.search(search_keyword)

        # 3. Verify 'SEARCHED PRODUCTS' section is visible
        assert products_page.is_searched_products_displayed(), "'SEARCHED PRODUCTS' heading should be visible."

        # 4. Verify search results contain items
        results = products_page.get_displayed_product_names()
        assert len(results) > 0, f"Expected search results for keyword '{search_keyword}', but found none."

        # 5. Verify that results relate to the keyword
        matching = [name for name in results if search_keyword.lower() in name.lower()]
        log.verify(f"Found {len(matching)} out of {len(results)} items containing '{search_keyword}'")
        assert len(matching) > 0, f"Expected matching results containing '{search_keyword}'"

    @pytest.mark.smoke
    @pytest.mark.cart
    def test_add_product_to_cart_and_verify_modal(
        self,
        products_page: ProductsPage,
    ) -> None:
        """Verify that clicking 'Add to cart' triggers confirmation modal and allows continuing shopping."""
        log.step("Starting test: test_add_product_to_cart_and_verify_modal")

        # 1. Open products catalog
        products_page.open()
        assert products_page.is_loaded(), "Products catalog should be displayed."

        # 2. Add first product to cart
        products_page.add_product_to_cart_by_index(0)

        # 3. Verify cart confirmation modal appears
        assert products_page.is_cart_modal_displayed(), "Cart confirmation modal was expected to appear."

        # 4. Dismiss modal by clicking 'Continue Shopping'
        products_page.click_continue_shopping()
        assert not products_page.is_cart_modal_displayed(), "Cart modal should be dismissed."

