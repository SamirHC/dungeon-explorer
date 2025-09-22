import pytest

from app.common.menu import MenuController, MenuOption, MenuPage


@pytest.fixture(scope="function")
def simple_menu() -> MenuPage:
    menu = MenuPage(
        label=0,
    )
    menu.add_option(MenuOption("0-0"))
    menu.add_option(MenuOption("0-1"))
    menu.add_option(MenuOption("0-2"))

    return menu


@pytest.fixture(scope="function")
def complex_menu() -> MenuPage:
    """
         0 [0, 1]
         1 [0 [0, 1, 2X, 3], 1]
    """
    # Page 0
    page0 = MenuPage("0")
    page0.add_option(opt0_0 := MenuOption("0-0"))
    page0.add_option(opt0_1 := MenuOption("0-1"))

    # Page 1
    page1 = MenuPage("1")
    page1.add_option(opt1_0 := MenuOption("1-0"))
    page1.add_option(opt1_1 := MenuOption("1-1"))

    # Page 1-0
    page1_0 = MenuPage("1-0")
    page1_0.add_option(opt1_0_0 := MenuOption("1-0-0"))
    page1_0.add_option(opt1_0_1 := MenuOption("1-0-1"))
    page1_0.add_option(opt1_0_2 := MenuOption("1-0-2", enabled=False))
    page1_0.add_option(opt1_0_3 := MenuOption("1-0-3"))

    # Connect
    MenuPage.connect_pages(page0, page1)
    opt1_0.set_child_menu(page1_0)
    
    return page0


def test_simple_menu_next_navigation(simple_menu: MenuPage):
    controller = MenuController(simple_menu)
    assert controller.current_option.label == "0-0"
    controller.next()
    assert controller.current_option.label == "0-1"
    controller.next()
    assert controller.current_option.label == "0-2"
    controller.next()
    assert controller.current_option.label == "0-0"


def test_simple_menu_prev_navigation(simple_menu: MenuPage):
    controller = MenuController(simple_menu)
    assert controller.current_option.label == "0-0"
    controller.prev()
    assert controller.current_option.label == "0-2"
    controller.prev()
    assert controller.current_option.label == "0-1"
    controller.prev()
    assert controller.current_option.label == "0-0"


def test_simple_menu_selection(simple_menu: MenuPage):
    controller = MenuController(simple_menu)
    assert controller.intent is None
    controller.select()
    assert controller.intent == "0-0"

    controller.next()
    controller.select()
    assert controller.intent == "0-1"


def test_simple_menu_next_page(simple_menu: MenuPage):
    controller = MenuController(simple_menu)
    controller.next_page()
    assert controller.current_option.label == "0-0"


def test_complex_menu_next_navigation(complex_menu: MenuPage):
    controller = MenuController(complex_menu)
    assert controller.current_option.label == "0-0"
    controller.next()
    assert controller.current_option.label == "0-1"
    controller.next()
    assert controller.current_option.label == "0-0"


def test_complex_menu_prev_navigation(complex_menu: MenuPage):
    controller = MenuController(complex_menu)
    assert controller.current_option.label == "0-0"
    controller.prev()
    assert controller.current_option.label == "0-1"
    controller.prev()
    assert controller.current_option.label == "0-0"


def test_complex_menu_selection(complex_menu: MenuPage):
    controller = MenuController(complex_menu)
    controller.next_page()
    controller.select()
    assert controller.intent is None
    assert controller.current_page.label == "1-0"

    controller.next()
    controller.select()
    assert controller.intent == "1-0-1"
    controller.consume_intent()

    controller.next()
    controller.select()
    assert controller.current_option.label == "1-0-2"
    assert controller.intent is None

    controller.next()
    controller.select()
    assert controller.intent == "1-0-3"


def test_complex_menu_parent_child_traversal(complex_menu: MenuPage):
    controller = MenuController(complex_menu)
    controller.next_page()
    assert controller.current_page.label == "1"
    controller.select()
    assert controller.current_page.label == "1-0"
    controller.back()
    assert controller.current_page.label == "1"

    controller.select()
    assert controller.current_page.label == "1-0"
    assert controller.current_option.label == "1-0-0"
    controller.next()
    controller.next()
    assert controller.current_option.label == "1-0-2"
    controller.back()
    assert controller.current_page.label == "1"


if __name__ == "__main__":
    import sys
    pytest.main(sys.argv)
