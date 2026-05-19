import time

import pytest
from alttester import AltDriver, By


@pytest.fixture(scope="module")
def alt_driver():
    driver = AltDriver()
    yield driver
    driver.stop()


def get_player(driver):
    return driver.wait_for_object(By.NAME, "Player", timeout=10)


def get_bridge(driver):
    return driver.wait_for_object(By.NAME, "TestInputBridge", timeout=10)


def get_player_x(driver):
    return get_player(driver).worldX


def get_player_y(driver):
    return get_player(driver).worldY


def call_bridge_method(bridge, method_name):
    return bridge.call_component_method(
        "TestInputBridge",
        method_name,
        "Assembly-CSharp",
        parameters=[]
    )


def reset_player(driver):
    bridge = get_bridge(driver)
    call_bridge_method(bridge, "ResetPlayerForTest")
    time.sleep(0.5)


def get_player_flip_x(driver):
    player = get_player(driver)

    try:
        return player.get_component_property(
            "UnityEngine.SpriteRenderer",
            "flipX",
            "UnityEngine"
        )
    except Exception:
        return player.get_component_property(
            "SpriteRenderer",
            "flipX",
            "UnityEngine"
        )


def test_tc_mj_001_player_moves_left_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)
    before_x = get_player_x(alt_driver)

    call_bridge_method(bridge, "MoveLeftForTest")
    time.sleep(1.3)

    after_x = get_player_x(alt_driver)

    assert after_x < before_x, (
        f"TC-MJ-001 실패: 좌측 이동 입력값 주입 후 X 좌표가 감소해야 함. "
        f"이동 전 X={before_x}, 이동 후 X={after_x}"
    )


def test_tc_mj_002_player_moves_right_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)
    before_x = get_player_x(alt_driver)

    call_bridge_method(bridge, "MoveRightForTest")
    time.sleep(1.3)

    after_x = get_player_x(alt_driver)

    assert after_x > before_x, (
        f"TC-MJ-002 실패: 우측 이동 입력값 주입 후 X 좌표가 증가해야 함. "
        f"이동 전 X={before_x}, 이동 후 X={after_x}"
    )


def test_tc_mj_003_player_stops_after_move_input_released_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)
    start_x = get_player_x(alt_driver)

    call_bridge_method(bridge, "MoveRightForTest")
    time.sleep(1.3)

    moved_x = get_player_x(alt_driver)

    call_bridge_method(bridge, "StopMoveForTest")
    time.sleep(0.7)

    stopped_x = get_player_x(alt_driver)

    move_distance = abs(moved_x - start_x)
    stop_distance = abs(stopped_x - moved_x)

    assert move_distance > 0.1, (
        f"TC-MJ-003 사전 이동 실패: 정지 검증 전 우측 이동이 발생해야 함. "
        f"시작 X={start_x}, 이동 후 X={moved_x}"
    )

    assert stop_distance < 0.2, (
        f"TC-MJ-003 실패: 정지 입력값 주입 후 위치 변화량이 작아야 함. "
        f"정지 전 X={moved_x}, 정지 후 X={stopped_x}, 변화량={stop_distance}"
    )


def test_tc_mj_004_player_direction_changes_left_and_right_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)

    call_bridge_method(bridge, "MoveRightForTest")
    time.sleep(1.0)
    right_flip_x = get_player_flip_x(alt_driver)

    call_bridge_method(bridge, "MoveLeftForTest")
    time.sleep(1.0)
    left_flip_x = get_player_flip_x(alt_driver)

    assert right_flip_x != left_flip_x, (
        f"TC-MJ-004 실패: 좌우 이동 입력값 변경 시 SpriteRenderer flipX 값이 변경되어야 함. "
        f"우측 이동 flipX={right_flip_x}, 좌측 이동 flipX={left_flip_x}"
    )


def test_tc_mj_005_player_basic_jump_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)
    before_y = get_player_y(alt_driver)

    call_bridge_method(bridge, "JumpForTest")
    time.sleep(0.4)

    jump_y = get_player_y(alt_driver)

    time.sleep(1.2)
    after_y = get_player_y(alt_driver)

    assert jump_y > before_y + 0.2, (
        f"TC-MJ-005 실패: 점프 입력값 주입 후 Y 좌표가 증가해야 함. "
        f"점프 전 Y={before_y}, 점프 중 Y={jump_y}"
    )

    assert after_y <= jump_y, (
        f"TC-MJ-005 실패: 점프 후 Player가 하강 또는 착지 방향으로 이동해야 함. "
        f"점프 중 Y={jump_y}, 이후 Y={after_y}"
    )


def test_tc_mj_006_player_moves_right_while_jumping_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)
    before_x = get_player_x(alt_driver)
    before_y = get_player_y(alt_driver)

    call_bridge_method(bridge, "MoveRightAndJumpForTest")
    time.sleep(1.0)

    after_x = get_player_x(alt_driver)
    after_y = get_player_y(alt_driver)

    assert after_x > before_x, (
        f"TC-MJ-006 실패: 이동 중 점프 시 X 좌표가 증가해야 함. "
        f"점프 전 X={before_x}, 점프 후 X={after_x}"
    )

    assert after_y > before_y, (
        f"TC-MJ-006 실패: 이동 중 점프 시 Y 좌표가 증가해야 함. "
        f"점프 전 Y={before_y}, 점프 후 Y={after_y}"
    )


def test_tc_mj_007_player_cannot_double_jump_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)
    start_y = get_player_y(alt_driver)

    call_bridge_method(bridge, "JumpForTest")
    time.sleep(0.25)

    first_jump_y = get_player_y(alt_driver)

    call_bridge_method(bridge, "JumpForTest")
    time.sleep(0.25)

    second_jump_y = get_player_y(alt_driver)

    first_delta = first_jump_y - start_y
    second_delta = second_jump_y - first_jump_y

    assert first_delta > 0.1, (
        f"TC-MJ-007 사전 점프 실패: 첫 번째 점프 후 Y 좌표가 증가해야 함. "
        f"시작 Y={start_y}, 첫 점프 Y={first_jump_y}"
    )

    assert second_delta <= first_delta + 0.3, (
        f"TC-MJ-007 실패: 공중 추가 점프가 제한되어야 함. "
        f"첫 점프 상승량={first_delta}, 두 번째 입력 후 추가 상승량={second_delta}"
    )


def test_tc_mj_008_player_opposite_direction_input_is_stable_by_bridge(alt_driver):
    reset_player(alt_driver)

    bridge = get_bridge(alt_driver)
    before_x = get_player_x(alt_driver)

    call_bridge_method(bridge, "MoveBothDirectionsForTest")
    time.sleep(1.2)

    after_x = get_player_x(alt_driver)
    distance = abs(after_x - before_x)

    assert distance < 0.2, (
        f"TC-MJ-008 실패: 좌우 동시 입력값 주입 시 비정상 이동이 없어야 함. "
        f"입력 전 X={before_x}, 입력 후 X={after_x}, 변화량={distance}"
    )