using UnityEngine;

public class GateController : MonoBehaviour
{
    [SerializeField] private DeviceInteractable unlockSource;

    private bool isUnlocked;

    private void OnEnable()
    {
        if (unlockSource != null)
        {
            unlockSource.Completed += Unlock;
        }
    }

    private void OnDisable()
    {
        if (unlockSource != null)
        {
            unlockSource.Completed -= Unlock;
        }
    }

    private void Unlock()
    {
        if (isUnlocked)
            return;

        isUnlocked = true;

        Debug.Log($"{gameObject.name} unlocked.");

        gameObject.SetActive(false);
    }
}