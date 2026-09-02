using System;
using System.Collections.Generic;

[Serializable]
public class InteractableConfig
{
    public string id;
    public string displayName;
    public int requiredInteractions;
    public bool deactivateOnComplete;
}

[Serializable]
public class InteractableConfigCollection
{
    public List<InteractableConfig> interactables;
}