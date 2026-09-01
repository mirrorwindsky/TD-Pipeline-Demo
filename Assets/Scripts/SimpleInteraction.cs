using UnityEngine;
using UnityEngine.InputSystem;

public class SimpleInteraction : MonoBehaviour
{
    [SerializeField] private float interactionDistance = 2f;

    private void Update()
    {
        Vector3 origin = transform.position + Vector3.down * 0.5f;
        Vector3 direction = transform.forward;

        Debug.DrawRay(
            origin,
            direction * interactionDistance,
            Color.red
        );

        if (Keyboard.current.eKey.wasPressedThisFrame)
        {
            Debug.Log("E pressed");
            TryInteract(origin, direction);
        }
    }

    private void TryInteract(Vector3 origin, Vector3 direction)
    {
        if (Physics.Raycast(
            origin,
            direction,
            out RaycastHit hit,
            interactionDistance))
        {
            Debug.Log($"Raycast hit: {hit.collider.name}");

            if (hit.collider.CompareTag("Interactable"))
            {
                Debug.Log($"Interacted with {hit.collider.name}");
                hit.collider.gameObject.SetActive(false);
            }
        }
        else
        {
            Debug.Log("Raycast hit nothing");
        }
    }
}