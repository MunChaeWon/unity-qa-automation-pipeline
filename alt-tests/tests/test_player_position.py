import pytest
from alttester import AltDriver, By


@pytest.fixture(scope="module")
def alt_driver():
    driver = AltDriver()
    yield driver
    driver.stop()


def test_player_position_can_be_read(alt_driver):
    player = alt_driver.wait_for_object(By.NAME, "Player", timeout=10)

    print(f"Player name: {player.name}")
    print(f"Player world position: x={player.worldX}, y={player.worldY}, z={player.worldZ}")

    assert player.name == "Player"
    assert player.worldX is not None
    assert player.worldY is not None