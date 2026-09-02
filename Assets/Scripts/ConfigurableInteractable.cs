using UnityEngine;

public class ConfigurableInteractable : MonoBehaviour
{
    [SerializeField] private string configId;
    [SerializeField] private InteractableConfigDatabase database;

    private InteractableConfig config;
    private int interactionCount;

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
        interactionCount++;

        Debug.Log(
            $"{config.displayName}: " +
            $"{interactionCount}/{config.requiredInteractions}"
        );

        if (interactionCount >= config.requiredInteractions
            && config.deactivateOnComplete)
        {
            gameObject.SetActive(false);
        }
    }
}