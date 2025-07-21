"""End-to-end tests for Meal Tracker Flask app using Playwright"""

import os
import pytest
from playwright.sync_api import Page, expect

APP_URL = os.environ.get("APP_URL", "http://localhost:5000")


class TestMealTracker:
    """Playwright e23 tests for the Meal Tracker app"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, page: Page):
        """Setup and teardown for each test"""
        # Setup: Navigate to the app
        page.goto(APP_URL)
        yield
        # Teardown: Clean up any test data if needed
        # Note: You might want to add cleanup logic here depending on your needs

    def test_full_e2e_workflow(self, page: Page):
        """Complete end-to-end test simulating all features"""

        # check that the page title contains "Meal Tracker"
        expect(page).to_have_title("Meal Tracker")

        # check that the main heading is visible
        heading = page.locator("h1")
        expect(heading).to_contain_text("Meal Tracker")

        # Check that the form elements are present
        expect(page.locator('input[name="meal"]')).to_be_visible()
        expect(page.locator('select[name="rating"]')).to_be_visible()
        expect(page.locator('input[type="submit"]')).to_be_visible()

        # test 1: Add meal
        page.fill('input[name="meal"]', "Chicken and potatoes")
        page.select_option('select[name="rating"]', "Okay")
        page.click('input[type="submit"]')

        expect(page.locator("text=Chicken and potatoes: Okay")).to_be_visible()

        # test 2: Delete the first meal
        # Find the <p> with the meal text, then go to its parent <div>, then the button
        meal_p = page.locator("p", has_text="Chicken and potatoes")
        meal_div = meal_p.locator("..")  # parent div
        delete_button = meal_div.locator('button[type="submit"]')
        delete_button.click()

        # verify first meal is gone
        expect(page.locator("text=Chicken and potatoes")).not_to_be_visible()

        # test 3: Add multiple meals
        meals_to_add = [
            ("fried macaroni bites", "DELICIOUS"),
            ("Pesto tortellini", "Pretty Good"),
            ("Taco Bell bean and cheese burrito", "Didn't really like it"),
            ("Bartlett tuna casserole", "Nasty"),
        ]

        for meal, rating in meals_to_add:
            page.fill('input[name="meal"]', meal)
            page.select_option('select[name="rating"]', rating)
            page.click('input[type="submit"]')

            # verify all of the meals appear
            expect(page.locator(f"text={meal}: {rating}")).to_be_visible()

        # test 4: delete specific meals
        # delete "fried macaroni bites"
        mac_p = page.locator("p", has_text="fried macaroni bites")
        macaroni_div = mac_p.locator("..")  # parent div
        macaroni_delete = macaroni_div.locator('button[type="submit"]')
        macaroni_delete.click()
        # verify it's gone
        expect(page.locator("text=fried macaroni bites")).not_to_be_visible()

        # verify other meals are still there
        expect(page.locator("text=Pesto tortellini")).to_be_visible()
        expect(page.locator("text=Taco Bell bean and cheese burrito")).to_be_visible()
        expect(page.locator("text=Bartlett tuna casserole")).to_be_visible()

        # Try to submit without filling required fields
        page.click('input[type="submit"]')

        # The form should not submit and we should still be on the same page
        expect(page.locator('input[name="meal"]')).to_be_visible()

        # Fill meal but not rating
        page.fill('input[name="meal"]', "Test meal")
        page.click('input[type="submit"]')

        # Should still be on the form page
        expect(page.locator('input[name="meal"]')).to_be_visible()

    def test_meal_history_section(self, page: Page):
        """Test that the meal history section displays correctly"""

        # Check that the meal history heading is present
        expect(page.locator("h2")).to_contain_text("Meal History")

        # Add a meal and verify it appears in the history section
        page.fill('input[name="meal"]', "History test meal")
        page.select_option('select[name="rating"]', "Pretty Good")
        page.click('input[type="submit"]')

        # The meal should appear with the bullet point format
        expect(page.locator("text=• History test meal: Pretty Good")).to_be_visible()


# Pytest configuration for Playwright
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
    }
