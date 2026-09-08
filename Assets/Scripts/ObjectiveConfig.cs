using System;
using System.Collections.Generic;

[Serializable]
public class ObjectiveConfig
{
    public string id;
    public string displayName;
    public string description;
}

[Serializable]
public class ObjectiveConfigCollection
{
    public List<ObjectiveConfig> objectives;
}