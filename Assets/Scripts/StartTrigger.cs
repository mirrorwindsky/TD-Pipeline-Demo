using UnityEngine;

public class StartTrigger : MonoBehaviour
{
    [SerializeField] private DemoFlowController flowController;

    private void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            flowController.StartMission();
        }
    }
}