using System;
using System.Collections.Generic;

[Serializable]
public class InteractableConfig
{
    public string id;
    public string displayName;

    public string interactionType;

    public int requiredInteractions;

    public string requiredItemId;
    public string grantedItemId;

    public string blockedMessage;
    public string completionMessage;

    public bool deactivateOnComplete;
}

[Serializable]
public class InteractableConfigCollection
{
    public List<InteractableConfig> interactables;
}