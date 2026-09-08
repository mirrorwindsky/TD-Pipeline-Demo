using System.Collections.Generic;
using UnityEngine;

public class ObjectiveConfigDatabase : MonoBehaviour
{
    [SerializeField] private TextAsset configFile;

    private Dictionary<string, ObjectiveConfig> objectiveById;

    private void Awake()
    {
        ObjectiveConfigCollection collection =
            JsonUtility.FromJson<ObjectiveConfigCollection>(
                configFile.text
            );

        objectiveById = new Dictionary<string, ObjectiveConfig>();

        foreach (ObjectiveConfig objective in collection.objectives)
        {
            objectiveById[objective.id] = objective;
        }
    }

    public bool TryGetObjective(
        string id,
        out ObjectiveConfig objective)
    {
        return objectiveById.TryGetValue(id, out objective);
    }
}