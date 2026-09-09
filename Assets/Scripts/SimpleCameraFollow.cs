using UnityEngine;
using UnityEngine.InputSystem;

[DefaultExecutionOrder(-100)]
public class SimpleCameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField, Min(0.5f)] private float cameraDistance = 3.5f;
    [SerializeField] private float focusHeight = 1f;
    [SerializeField, Min(0.01f)] private float mouseSensitivity = 0.12f;
    [SerializeField] private float initialPitch = 12f;
    [SerializeField, Range(-60f, 0f)] private float minPitch = -15f;
    [SerializeField, Range(0f, 60f)] private float maxPitch = 40f;
    [SerializeField, Min(0.1f)] private float followSpeed = 8f;
    [SerializeField, Min(0.05f)] private float collisionRadius = 0.3f;

    private float yaw;
    private float pitch;
    private float currentDistance;
    private Vector3 focusPosition;

    private void OnEnable()
    {
        if (target == null)
            return;

        yaw = target.eulerAngles.y;
        pitch = Mathf.Clamp(initialPitch, minPitch, maxPitch);
        focusPosition = target.position + Vector3.up * focusHeight;
        currentDistance = cameraDistance;

        // Start at the playable view instead of sweeping down from the old pose.
        UpdateCamera(1f);
        SetCursorLocked(true);
    }

    private void Update()
    {
        if (target == null)
            return;

        if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
        {
            SetCursorLocked(false);
            return;
        }

        // Escape / lost focus releases the cursor. Click the Game view to resume.
        if (Cursor.lockState != CursorLockMode.Locked)
        {
            if (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame)
                SetCursorLocked(true);

            return;
        }

        if (Mouse.current != null)
        {
            // Mouse delta is already per-frame pixel displacement; no deltaTime.
            Vector2 look = Mouse.current.delta.ReadValue() * mouseSensitivity;
            yaw = Mathf.Repeat(yaw + look.x, 360f);
            pitch = Mathf.Clamp(pitch - look.y, minPitch, maxPitch);
        }

        // Run before movement / interaction so the forward ray uses this yaw.
        target.rotation = Quaternion.Euler(0f, yaw, 0f);
    }

    private void LateUpdate()
    {
        if (target == null)
            return;

        float t = 1f - Mathf.Exp(-followSpeed * Time.deltaTime);
        focusPosition = Vector3.Lerp(
            focusPosition,
            target.position + Vector3.up * focusHeight,
            t
        );

        UpdateCamera(t);
    }

    private void UpdateCamera(float t)
    {
        Quaternion rotation = Quaternion.Euler(pitch, yaw, 0f);
        Vector3 backward = rotation * Vector3.back;
        float allowedDistance = cameraDistance;

        // Existing walls can be closer than the normal follow distance.
        RaycastHit[] hits = Physics.SphereCastAll(
            focusPosition,
            collisionRadius,
            backward,
            cameraDistance,
            Physics.DefaultRaycastLayers,
            QueryTriggerInteraction.Ignore
        );

        foreach (RaycastHit hit in hits)
        {
            if (hit.transform == target || hit.transform.IsChildOf(target))
                continue;

            allowedDistance = Mathf.Min(allowedDistance, Mathf.Max(0f, hit.distance - 0.05f));
        }

        // Pull in immediately at a wall; ease back out once the space is clear.
        currentDistance = allowedDistance < currentDistance
            ? allowedDistance
            : Mathf.Lerp(currentDistance, allowedDistance, t);

        transform.SetPositionAndRotation(focusPosition + backward * currentDistance, rotation);
    }

    private void OnApplicationFocus(bool hasFocus)
    {
        if (!hasFocus)
            SetCursorLocked(false);
    }

    private void OnDisable()
    {
        SetCursorLocked(false);
    }

    private static void SetCursorLocked(bool locked)
    {
        Cursor.lockState = locked ? CursorLockMode.Locked : CursorLockMode.None;
        Cursor.visible = !locked;
    }
}
