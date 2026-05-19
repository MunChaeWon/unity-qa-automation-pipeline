using System.Collections;
using System.Reflection;
using UnityEngine;

public class TestInputBridge : MonoBehaviour
{
    [Header("Test Target")]
    [SerializeField] private GameObject playerObject;

    private Component playerController;

    private FieldInfo moveField;
    private FieldInfo jumpField;
    private FieldInfo stopJumpField;
    private FieldInfo velocityField;
    private FieldInfo targetVelocityField;
    private FieldInfo jumpStateField;

    private MethodInfo computeVelocityMethod;

    private Coroutine moveCoroutine;
    private Vector3 initialPlayerPosition;
    private bool initialPositionSaved;

    private void Awake()
    {
        InitializeReferences();
    }

    private void Start()
    {
        InitializeReferences();
    }

    private void InitializeReferences()
    {
        if (playerObject == null)
        {
            playerObject = GameObject.Find("Player");
        }

        if (playerObject == null)
        {
            Debug.LogError("TestInputBridge: Player 오브젝트를 찾을 수 없음");
            return;
        }

        if (!initialPositionSaved)
        {
            initialPlayerPosition = playerObject.transform.position;
            initialPositionSaved = true;
        }

        playerController = playerObject.GetComponent("PlayerController");

        if (playerController == null)
        {
            Debug.LogError("TestInputBridge: PlayerController 컴포넌트를 찾을 수 없음");
            return;
        }

        System.Type controllerType = playerController.GetType();

        moveField = FindFieldInHierarchy(controllerType, "move");
        jumpField = FindFieldInHierarchy(controllerType, "jump");
        stopJumpField = FindFieldInHierarchy(controllerType, "stopJump");
        velocityField = FindFieldInHierarchy(controllerType, "velocity");
        targetVelocityField = FindFieldInHierarchy(controllerType, "targetVelocity");
        jumpStateField = FindFieldInHierarchy(controllerType, "jumpState");

        computeVelocityMethod = FindMethodInHierarchy(controllerType, "ComputeVelocity");

        if (moveField == null)
        {
            Debug.LogError("TestInputBridge: move 필드를 찾을 수 없음");
        }

        if (jumpField == null)
        {
            Debug.LogError("TestInputBridge: jump 필드를 찾을 수 없음");
        }

        if (velocityField == null)
        {
            Debug.LogError("TestInputBridge: velocity 필드를 찾을 수 없음");
        }

        if (computeVelocityMethod == null)
        {
            Debug.LogError("TestInputBridge: ComputeVelocity 메서드를 찾을 수 없음");
        }
    }

    public void ResetPlayerForTest()
    {
        InitializeReferences();

        if (moveCoroutine != null)
        {
            StopCoroutine(moveCoroutine);
            moveCoroutine = null;
        }

        if (playerObject == null)
        {
            return;
        }

        playerObject.transform.position = initialPlayerPosition;

        SetMoveValue(0f);
        SetVelocity(Vector2.zero);
        SetTargetVelocity(Vector2.zero);
        SetBoolField(jumpField, false);
        SetBoolField(stopJumpField, false);
        ResetJumpStateToGrounded();

        InvokeComputeVelocity();
    }

    public void MoveLeftForTest()
    {
        StartMoveForTest(-1f, 1.0f);
    }

    public void MoveRightForTest()
    {
        StartMoveForTest(1f, 1.0f);
    }

    public void StopMoveForTest()
    {
        StartMoveForTest(0f, 0.2f);
    }

    public void MoveBothDirectionsForTest()
    {
        StartMoveForTest(0f, 1.0f);
    }

    public void JumpForTest()
    {
        InitializeReferences();

        if (playerController == null)
        {
            return;
        }

        SetBoolField(jumpField, true);
        InvokeComputeVelocity();
    }

    public void MoveRightAndJumpForTest()
    {
        InitializeReferences();

        if (moveCoroutine != null)
        {
            StopCoroutine(moveCoroutine);
        }

        moveCoroutine = StartCoroutine(MoveAndJumpForSeconds(1f, 1.0f));
    }

    public void StartMoveForTest(float direction, float duration)
    {
        InitializeReferences();

        if (moveCoroutine != null)
        {
            StopCoroutine(moveCoroutine);
        }

        moveCoroutine = StartCoroutine(MoveForSeconds(direction, duration));
    }

    private IEnumerator MoveForSeconds(float direction, float duration)
    {
        float endTime = Time.time + duration;

        while (Time.time < endTime)
        {
            ApplyMove(direction);
            yield return null;
        }

        ApplyMove(0f);
        moveCoroutine = null;
    }

    private IEnumerator MoveAndJumpForSeconds(float direction, float duration)
    {
        float endTime = Time.time + duration;
        bool jumpApplied = false;

        while (Time.time < endTime)
        {
            ApplyMove(direction);

            if (!jumpApplied)
            {
                JumpForTest();
                jumpApplied = true;
            }

            yield return null;
        }

        ApplyMove(0f);
        moveCoroutine = null;
    }

    private void ApplyMove(float direction)
    {
        SetMoveValue(direction);
        InvokeComputeVelocity();
    }

    private void SetMoveValue(float direction)
    {
        if (playerController == null || moveField == null)
        {
            return;
        }

        Vector2 moveValue = Vector2.zero;
        moveValue.x = direction;
        moveField.SetValue(playerController, moveValue);
    }

    private void SetVelocity(Vector2 velocity)
    {
        if (playerController == null || velocityField == null)
        {
            return;
        }

        velocityField.SetValue(playerController, velocity);
    }

    private void SetTargetVelocity(Vector2 targetVelocity)
    {
        if (playerController == null || targetVelocityField == null)
        {
            return;
        }

        targetVelocityField.SetValue(playerController, targetVelocity);
    }

    private void SetBoolField(FieldInfo fieldInfo, bool value)
    {
        if (playerController == null || fieldInfo == null)
        {
            return;
        }

        fieldInfo.SetValue(playerController, value);
    }

    private void ResetJumpStateToGrounded()
    {
        if (playerController == null || jumpStateField == null)
        {
            return;
        }

        System.Type enumType = jumpStateField.FieldType;

        if (!enumType.IsEnum)
        {
            return;
        }

        object groundedValue = System.Enum.Parse(enumType, "Grounded");
        jumpStateField.SetValue(playerController, groundedValue);
    }

    private void InvokeComputeVelocity()
    {
        if (playerController == null || computeVelocityMethod == null)
        {
            return;
        }

        computeVelocityMethod.Invoke(playerController, null);
    }

    private FieldInfo FindFieldInHierarchy(System.Type type, string fieldName)
    {
        while (type != null)
        {
            FieldInfo field = type.GetField(
                fieldName,
                BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public
            );

            if (field != null)
            {
                return field;
            }

            type = type.BaseType;
        }

        return null;
    }

    private MethodInfo FindMethodInHierarchy(System.Type type, string methodName)
    {
        while (type != null)
        {
            MethodInfo method = type.GetMethod(
                methodName,
                BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public
            );

            if (method != null)
            {
                return method;
            }

            type = type.BaseType;
        }

        return null;
    }
}