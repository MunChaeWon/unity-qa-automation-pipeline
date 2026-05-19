import pytest
from alttester import AltDriver, By


@pytest.fixture(scope="module")
def alt_driver():
    driver = AltDriver()
    yield driver
    driver.stop()


def test_alttester_connection_and_find_player(alt_driver):
    player = alt_driver.wait_for_object(By.NAME, "Player", timeout=10)

    assert player is not None
    assert player.name == "Player"