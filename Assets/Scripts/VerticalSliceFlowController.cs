using UnityEngine;

public class VerticalSliceFlowController : MonoBehaviour
{
    [SerializeField] private PlayerHUD hud;
    [SerializeField] private ObjectiveConfigDatabase objectiveDatabase;

    [SerializeField] private PickupInteractable powerCell;
    [SerializeField] private DeviceInteractable powerNode;
    [SerializeField] private DeviceInteractable controlTerminal;

    private bool missionCompleted;

    private void OnEnable()
    {
        powerCell.PickedUp += OnPowerCellPickedUp;
        powerNode.Completed += OnPowerNodeCompleted;
        controlTerminal.Completed += OnControlTerminalCompleted;
    }

    private void OnDisable()
    {
        powerCell.PickedUp -= OnPowerCellPickedUp;
        powerNode.Completed -= OnPowerNodeCompleted;
        controlTerminal.Completed -= OnControlTerminalCompleted;
    }

    private void Start()
    {
        SetObjective("find_power_cell");
    }

    private void OnPowerCellPickedUp()
    {
        SetObjective("repair_power_node");
    }

    private void OnPowerNodeCompleted()
    {
        SetObjective("activate_control_terminal");
    }

    private void OnControlTerminalCompleted()
    {
        SetObjective("reach_exit");
    }

    public void TryCompleteMission()
    {
        if (missionCompleted)
            return;

        // 防止以后因为关卡漏洞绕过 ExitDoor 后提前完成任务
        if (!controlTerminal.IsCompleted)
        {
            hud.ShowFeedback(
                "The exit is not unlocked yet."
            );
            return;
        }

        missionCompleted = true;

        SetObjective("mission_complete");
        hud.ShowMissionComplete();

        hud.ShowFeedback(
            "Facility restored. Exit reached.",
            4f
        );

        Debug.Log("Vertical Slice Complete!");
    }

    private void SetObjective(string objectiveId)
    {
        if (!objectiveDatabase.TryGetObjective(
            objectiveId,
            out ObjectiveConfig objective))
        {
            Debug.LogError(
                $"Objective config not found: {objectiveId}",
                this
            );
            return;
        }

        hud.SetObjective(objective.description);
    }
}
