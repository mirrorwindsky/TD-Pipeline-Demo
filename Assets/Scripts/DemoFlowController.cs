using UnityEngine;

public class DemoFlowController : MonoBehaviour
{
    [SerializeField] private ConfigurableInteractable quickCube;
    [SerializeField] private ConfigurableInteractable sturdyCube;
    [SerializeField] private GameObject exitDoor;

    private bool missionStarted;
    private bool exitUnlocked;
    private bool missionCompleted;

    private int completedObjectives;

    private const int RequiredObjectives = 2;

    private void OnEnable()
    {
        quickCube.Completed += OnObjectiveCompleted;
        sturdyCube.Completed += OnObjectiveCompleted;
    }

    private void OnDisable()
    {
        quickCube.Completed -= OnObjectiveCompleted;
        sturdyCube.Completed -= OnObjectiveCompleted;
    }

    public void StartMission()
    {
        if (missionStarted)
            return;

        missionStarted = true;

        Debug.Log("Mission started: complete both interactables.");
    }

    private void OnObjectiveCompleted()
    {
        if (!missionStarted)
            return;

        completedObjectives++;

        Debug.Log(
            $"Objective completed: " +
            $"{completedObjectives}/{RequiredObjectives}"
        );

        if (completedObjectives >= RequiredObjectives)
        {
            exitUnlocked = true;
            exitDoor.SetActive(false);

            Debug.Log("All objectives complete. Exit opened.");
        }
    }

    public void TryFinishMission()
    {
        if (!missionStarted)
            return;

        if (!exitUnlocked)
        {
            Debug.Log("Exit reached, but objectives are not complete.");
            return;
        }

        if (missionCompleted)
            return;

        missionCompleted = true;

        Debug.Log("Demo Complete!");
    }
}