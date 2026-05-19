// Assets/Tests/EditMode/PlayerHealthTest.cs
// 플레이어 체력 계산 로직을 검증하는 Edit Mode 테스트
using NUnit.Framework;
// UnityEngine.Mathf 대신 System.Math.Max를 사용하기 위해 UnityEngine 참조는 필요 없습니다.

public class PlayerHealthTest
{
    [Test]
    public void PlayerHealth_WhenDamageTaken_HealthDecreases()
    {
        // Arrange: 초기 체력과 데미지 설정
        int initialHealth = 100;
        int damage = 30;
        int expectedHealth = 70;

        // Act: 데미지 계산 수행
        PlayerHealth player = new PlayerHealth(initialHealth);
        player.TakeDamage(damage);
        int actualHealth = player.Health;

        // Assert: 결과가 예상치와 일치하는지 검증
        Assert.AreEqual(expectedHealth, actualHealth, 
            "데미지를 받은 후 체력이 올바르게 감소해야 합니다.");
    }

    [Test]
    public void PlayerHealth_WhenHealthBelowZero_ReturnZero()
    {
        // Arrange: 낮은 체력 상태 설정
        int currentHealth = 10;
        int damage = 50;
        int expectedHealth = 0;

        // Act: 체력이 0 이하로 내려가지 않도록 처리
        PlayerHealth player = new PlayerHealth(currentHealth);
        player.TakeDamage(damage);
        int actualHealth = player.Health;

        // Assert: 0 미만으로 내려가지 않았는지 검증
        Assert.AreEqual(expectedHealth, actualHealth, 
            "체력은 0 이하로 내려갈 수 없습니다.");
    }
}