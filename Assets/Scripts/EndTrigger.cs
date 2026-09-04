using UnityEngine;

public class EndTrigger : MonoBehaviour
{
    [SerializeField] private DemoFlowController flowController;

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            flowController.TryFinishMission();
        }
    }
}