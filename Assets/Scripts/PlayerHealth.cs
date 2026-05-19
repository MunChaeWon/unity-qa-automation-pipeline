// Assets/Scripts/PlayerHealth.cs

/// <summary>
/// 플레이어의 체력 관리 로직을 담당하는 클래스
/// </summary>
public class PlayerHealth
{
    private int _health;

    public PlayerHealth(int initialHealth)
    {
        _health = initialHealth;
    }

    public int Health => _health;

    public void TakeDamage(int damage)
    {
        _health = System.Math.Max(0, _health - damage); // 체력이 0 미만으로 내려가지 않도록 처리
    }
}