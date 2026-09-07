using System;
using UnityEngine;

public class PickupInteractable : MonoBehaviour, IInteractable
{
    [SerializeField] private string configId;
    [SerializeField] private InteractableConfigDatabase database;

    public event Action PickedUp;

    private InteractableConfig config;

    private void Start()
    {
        if (!database.TryGetConfig(configId, out config))
        {
            Debug.LogError(
                $"Config not found: {configId}",
                this
            );

            enabled = false;
        }
    }

    public void Interact(GameObject interactor)
    {
        PlayerInventory inventory =
            interactor.GetComponent<PlayerInventory>();

        PlayerHUD hud =
            interactor.GetComponent<PlayerHUD>();

        if (inventory == null)
        {
            Debug.LogError(
                $"Interactor has no PlayerInventory: {interactor.name}",
                this
            );
            return;
        }

        if (!inventory.AddItem(config.grantedItemId))
        {
            hud?.ShowFeedback(
                $"{config.displayName} is already in inventory."
            );
            return;
        }

        Debug.Log($"Picked up {config.displayName}.");

        hud?.ShowFeedback(config.completionMessage);

        PickedUp?.Invoke();

        if (config.deactivateOnComplete)
        {
            gameObject.SetActive(false);
        }
    }
}