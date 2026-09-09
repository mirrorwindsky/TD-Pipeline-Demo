using UnityEngine;
using UnityEngine.InputSystem;

[RequireComponent(typeof(CharacterController))]
[DefaultExecutionOrder(-50)]
public class SimplePlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float gravity = -20f;
    [Tooltip("Enable with the mouse camera: W/S move forward/back, A/D strafe. Leave off for the V1 fixed-camera baseline.")]
    [SerializeField] private bool usePlayerRelativeMovement;

    private CharacterController controller;
    private float verticalVelocity;

    private void Awake()
    {
        controller = GetComponent<CharacterController>();
    }

    private void Update()
    {
        Vector2 input = Vector2.zero;
        Keyboard keyboard = Keyboard.current;

        if (keyboard != null && (!usePlayerRelativeMovement || Cursor.lockState == CursorLockMode.Locked))
        {
            if (keyboard.wKey.isPressed)
                input.y += 1f;

            if (keyboard.sKey.isPressed)
                input.y -= 1f;

            if (keyboard.dKey.isPressed)
                input.x += 1f;

            if (keyboard.aKey.isPressed)
                input.x -= 1f;
        }

        Vector3 move = new Vector3(input.x, 0f, input.y).normalized;

        if (usePlayerRelativeMovement)
            move = transform.right * move.x + transform.forward * move.z;

        // CharacterController does not apply gravity automatically.
        if (controller.isGrounded && verticalVelocity < 0f)
        {
            verticalVelocity = -2f;
        }

        verticalVelocity += gravity * Time.deltaTime;

        Vector3 velocity = move * moveSpeed;
        velocity.y = verticalVelocity;

        controller.Move(velocity * Time.deltaTime);

        // The third-person camera owns facing, including while backing up / strafing.
        if (!usePlayerRelativeMovement && move.sqrMagnitude > 0.001f)
        {
            transform.forward = move;
        }
    }
}
