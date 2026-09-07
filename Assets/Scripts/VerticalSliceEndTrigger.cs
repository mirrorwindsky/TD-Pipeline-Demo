using UnityEngine;

public class VerticalSliceEndTrigger : MonoBehaviour
{
    [SerializeField]
    private VerticalSliceFlowController flowController;

    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player"))
            return;

        flowController.TryCompleteMission();
    }
}