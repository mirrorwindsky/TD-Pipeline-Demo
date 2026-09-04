using System;
using UnityEngine;

public class ConfigurableInteractable : MonoBehaviour
{
    [SerializeField] private string configId;
    [SerializeField] private InteractableConfigDatabase database;

    public event Action Completed;

    private InteractableConfig config;
    private int interactionCount;
    private bool isCompleted;

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

    public void Interact()
    {
        if (isCompleted)
            return;

        interactionCount++;

        Debug.Log(
            $"{config.displayName}: " +
            $"{interactionCount}/{config.requiredInteractions}"
        );

        if (interactionCount >= config.requiredInteractions)
        {
            isCompleted = true;

            Completed?.Invoke();

            if (config.deactivateOnComplete)
            {
                gameObject.SetActive(false);
            }
        }
    }
}