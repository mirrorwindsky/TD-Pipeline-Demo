using UnityEngine;

public class SimpleCameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target;

    [SerializeField]
    private Vector3 offset = new Vector3(0f, 8f, -7f);

    [SerializeField]
    private Vector3 lookOffset = new Vector3(0f, 1f, 0f);

    [SerializeField] private float followSpeed = 8f;

    private void LateUpdate()
    {
        if (target == null)
            return;

        Vector3 desiredPosition = target.position + offset;

        float t = 1f - Mathf.Exp(-followSpeed * Time.deltaTime);

        transform.position = Vector3.Lerp(
            transform.position,
            desiredPosition,
            t
        );

        transform.LookAt(target.position + lookOffset);
    }
}