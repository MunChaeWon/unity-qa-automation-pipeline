using System.Collections;
using System.Reflection;
using NUnit.Framework;
using Platformer.Mechanics;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class PlayerFunctionPlayModeTest
{
    private const string TestSceneName = "SampleScene";
    private const string PlayerTag = "Player";

    private PlayerController player;

    [UnitySetUp]
public IEnumerator SetUp()
{
    SceneManager.LoadScene(TestSceneName);
    yield return null;
    yield return new WaitForSeconds(0.5f);

    GameObject playerObject = GameObject.Find("Player");
    Assert.IsNotNull(playerObject, "Player 이름을 가진 오브젝트가 존재해야 합니다.");

    player = playerObject.GetComponent<PlayerController>();
    Assert.IsNotNull(player, "Player 오브젝트에 PlayerController 컴포넌트가 존재해야 합니다.");
}

    [UnityTest]
    public IEnumerator TC_001_PlayerObjectExists()
    {
        GameObject playerObject = GameObject.FindWithTag(PlayerTag);

        Assert.IsNotNull(playerObject, "Player 오브젝트가 씬에 존재해야 합니다.");
        Assert.AreEqual("Player", playerObject.name, "Player 오브젝트 이름이 Player여야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_002_PlayerControllerExists()
    {
        Assert.IsNotNull(player, "PlayerController 컴포넌트가 존재해야 합니다.");
        Assert.IsTrue(player.enabled, "PlayerController 컴포넌트가 활성화 상태여야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_003_PlayerControlEnabledByDefault()
    {
        Assert.IsTrue(player.controlEnabled, "게임 시작 시 플레이어 조작이 활성화 상태여야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_004_PlayerMaxSpeedIsValid()
    {
        Assert.Greater(player.maxSpeed, 0f, "플레이어 최대 이동 속도는 0보다 커야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_005_PlayerJumpSpeedIsValid()
    {
        Assert.Greater(player.jumpTakeOffSpeed, 0f, "플레이어 점프 속도는 0보다 커야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_006_PlayerMoveRight_TargetVelocityIncreases()
    {
        SetPrivateField(player, "move", new Vector2(1f, 0f));
        InvokeNonPublicMethod(player, "ComputeVelocity");

        Vector2 targetVelocity = GetTargetVelocity(player);

        Assert.Greater(targetVelocity.x, 0f, "우측 이동 입력 시 목표 X 속도가 양수로 설정되어야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_007_PlayerMoveLeft_TargetVelocityDecreases()
    {
        SetPrivateField(player, "move", new Vector2(-1f, 0f));
        InvokeNonPublicMethod(player, "ComputeVelocity");

        Vector2 targetVelocity = GetTargetVelocity(player);

        Assert.Less(targetVelocity.x, 0f, "좌측 이동 입력 시 목표 X 속도가 음수로 설정되어야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_008_PlayerMoveRight_SpriteFacesRight()
    {
        SpriteRenderer spriteRenderer = player.GetComponent<SpriteRenderer>();
        Assert.IsNotNull(spriteRenderer, "Player 오브젝트에 SpriteRenderer 컴포넌트가 존재해야 합니다.");

        SetPrivateField(player, "move", new Vector2(1f, 0f));
        InvokeNonPublicMethod(player, "ComputeVelocity");

        Assert.IsFalse(spriteRenderer.flipX, "우측 이동 입력 시 플레이어 스프라이트가 우측을 바라보아야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_009_PlayerMoveLeft_SpriteFacesLeft()
    {
        SpriteRenderer spriteRenderer = player.GetComponent<SpriteRenderer>();
        Assert.IsNotNull(spriteRenderer, "Player 오브젝트에 SpriteRenderer 컴포넌트가 존재해야 합니다.");

        SetPrivateField(player, "move", new Vector2(-1f, 0f));
        InvokeNonPublicMethod(player, "ComputeVelocity");

        Assert.IsTrue(spriteRenderer.flipX, "좌측 이동 입력 시 플레이어 스프라이트가 좌측을 바라보아야 합니다.");

        yield return null;
    }

    [UnityTest]
    public IEnumerator TC_010_PlayerHealthComponentExists()
    {
        Health health = player.GetComponent<Health>();

        Assert.IsNotNull(health, "Player 오브젝트에 Health 컴포넌트가 존재해야 합니다.");
        Assert.IsTrue(health.IsAlive, "게임 시작 시 플레이어 체력이 살아있는 상태여야 합니다.");

        yield return null;
    }

    private static void SetPrivateField(object target, string fieldName, object value)
    {
        FieldInfo field = target.GetType().GetField(
            fieldName,
            BindingFlags.Instance | BindingFlags.NonPublic
        );

        Assert.IsNotNull(field, $"{fieldName} 필드를 찾을 수 없습니다.");
        field.SetValue(target, value);
    }

    private static void InvokeNonPublicMethod(object target, string methodName)
    {
        MethodInfo method = target.GetType().GetMethod(
            methodName,
            BindingFlags.Instance | BindingFlags.NonPublic
        );

        Assert.IsNotNull(method, $"{methodName} 메서드를 찾을 수 없습니다.");
        method.Invoke(target, null);
    }

    private static Vector2 GetTargetVelocity(PlayerController target)
    {
        FieldInfo field = typeof(KinematicObject).GetField(
            "targetVelocity",
            BindingFlags.Instance | BindingFlags.NonPublic
        );

        Assert.IsNotNull(field, "targetVelocity 필드를 찾을 수 없습니다.");
        return (Vector2)field.GetValue(target);
    }
}