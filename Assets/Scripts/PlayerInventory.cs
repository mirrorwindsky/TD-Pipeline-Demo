using System.Collections.Generic;
using UnityEngine;

public class PlayerInventory : MonoBehaviour
{
    private readonly HashSet<string> items = new();

    public bool AddItem(string itemId)
    {
        bool added = items.Add(itemId);

        if (added)
        {
            Debug.Log($"Item acquired: {itemId}");
        }

        return added;
    }

    public bool HasItem(string itemId)
    {
        return items.Contains(itemId);
    }

    public bool RemoveItem(string itemId)
    {
        bool removed = items.Remove(itemId);

        if (removed)
        {
            Debug.Log($"Item consumed: {itemId}");
        }

        return removed;
    }
}