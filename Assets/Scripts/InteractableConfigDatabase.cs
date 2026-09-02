using System.Collections.Generic;
using UnityEngine;

public class InteractableConfigDatabase : MonoBehaviour
{
    [SerializeField] private TextAsset configFile;

    private Dictionary<string, InteractableConfig> configById;

    private void Awake()
    {
        InteractableConfigCollection collection =
            JsonUtility.FromJson<InteractableConfigCollection>(
                configFile.text
            );

        configById = new Dictionary<string, InteractableConfig>();

        foreach (InteractableConfig config in collection.interactables)
        {
            configById[config.id] = config;
        }
    }

    public bool TryGetConfig(
        string id,
        out InteractableConfig config)
    {
        return configById.TryGetValue(id, out config);
    }
}