import time
import pytest
from alttester import AltDriver, By, AltKeyCode

@pytest.fixture(scope="module")
def alt_driver():
    # AltTester 서버와 연결을 시도하옵니다.
    driver = AltDriver()
    yield driver
    # 테스트가 끝나면 연결을 안전하게 끊사옵니다.
    driver.stop()

def get_player_x(driver):
    # 'Player'라는 이름의 오브젝트를 찾아 그 X 좌표를 반환하옵니다.
    player = driver.wait_for_object(By.NAME, "Player", timeout=10)
    return player.worldX

def test_tc_mj_001_player_moves_left(alt_driver):
    # 1. 이동 전 좌표 기록
    before_x = get_player_x(alt_driver)
    print(f"\n[TC-MJ-001] 이동 전 X: {before_x}")

    # 2. 좌측 이동 (A 키를 꾹 누르는 시뮬레이션)
    alt_driver.key_down(AltKeyCode.A)
    time.sleep(1.0)  # 1초간 이동하옵니다.
    alt_driver.key_up(AltKeyCode.A)
    
    # 3. 이동 후 좌표 기록
    after_x = get_player_x(alt_driver)
    print(f"[TC-MJ-001] 이동 후 X: {after_x}")

    # 4. 검증: 좌측으로 갔다면 X 좌표가 감소해야 하옵니다.
    assert after_x < before_x, (
        f"TC-MJ-001 실패: 좌측 이동 후 X 좌표가 감소해야 함. "
        f"이동 전 X={before_x}, 이동 후 X={after_x}"
    )

def test_tc_mj_002_player_moves_right(alt_driver):
    # 1. 이동 전 좌표 기록
    before_x = get_player_x(alt_driver)
    print(f"\n[TC-MJ-002] 이동 전 X: {before_x}")

    # 2. 우측 이동 (D 키를 꾹 누르는 시뮬레이션)
    alt_driver.key_down(AltKeyCode.D)
    time.sleep(1.0)  # 1초간 이동하옵니다.
    alt_driver.key_up(AltKeyCode.D)

    # 3. 이동 후 좌표 기록
    after_x = get_player_x(alt_driver)
    print(f"[TC-MJ-002] 이동 후 X: {after_x}")

    # 4. 검증: 우측으로 갔다면 X 좌표가 증가해야 하옵니다.
    assert after_x > before_x, (
        f"TC-MJ-002 실패: 우측 이동 후 X 좌표가 증가해야 함. "
        f"이동 전 X={before_x}, 이동 후 X={after_x}"
    )