import time

import pytest
from alttester import AltDriver, By, AltKeyCode


@pytest.fixture(scope="module")
def alt_driver():
    driver = AltDriver()
    yield driver
    driver.stop()


def get_player_x(driver):
    player = driver.wait_for_object(By.NAME, "Player", timeout=10)
    return player.worldX


def test_tc_mj_001_player_moves_left(alt_driver):
    before_x = get_player_x(alt_driver)

    alt_driver.press_key(AltKeyCode.A, duration=0.7)
    time.sleep(0.5)

    after_x = get_player_x(alt_driver)

    assert after_x < before_x, (
        f"TC-MJ-001 실패: 좌측 이동 후 X 좌표가 감소해야 함. "
        f"이동 전 X={before_x}, 이동 후 X={after_x}"
    )


def test_tc_mj_002_player_moves_right(alt_driver):
    before_x = get_player_x(alt_driver)

    alt_driver.press_key(AltKeyCode.D, duration=0.7)
    time.sleep(0.5)

    after_x = get_player_x(alt_driver)

    assert after_x > before_x, (
        f"TC-MJ-002 실패: 우측 이동 후 X 좌표가 증가해야 함. "
        f"이동 전 X={before_x}, 이동 후 X={after_x}"
    )