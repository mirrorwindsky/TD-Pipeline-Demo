using UnityEngine;
using UnityEngine.InputSystem;

public class SimpleInteraction : MonoBehaviour
{
    [SerializeField] private float interactionDistance = 2f;
    [SerializeField] private PlayerHUD hud;

    private void Update()
    {
        Vector3 origin =
            transform.position + Vector3.down * 0.5f;

        Vector3 direction = transform.forward;

        Debug.DrawRay(
            origin,
            direction * interactionDistance,
            Color.red
        );

        IInteractable interactable =
            FindInteractable(origin, direction);

        if (interactable != null)
        {
            hud?.SetPrompt("Press E to interact");
        }
        else
        {
            hud?.SetPrompt("");
        }

        if (Keyboard.current.eKey.wasPressedThisFrame &&
            interactable != null)
        {
            interactable.Interact(gameObject);
        }
    }

    private IInteractable FindInteractable(
        Vector3 origin,
        Vector3 direction)
    {
        if (!Physics.Raycast(
                origin,
                direction,
                out RaycastHit hit,
                interactionDistance))
        {
            return null;
        }

        if (!hit.collider.CompareTag("Interactable"))
        {
            return null;
        }

        return hit.collider.GetComponent<IInteractable>();
    }
}