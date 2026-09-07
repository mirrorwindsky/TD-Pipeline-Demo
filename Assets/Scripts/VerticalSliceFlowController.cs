using UnityEngine;

public class VerticalSliceFlowController : MonoBehaviour
{
    [SerializeField] private PlayerHUD hud;

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
        hud.SetObjective(
            "Objective: Find a Power Cell in Storage."
        );
    }

    private void OnPowerCellPickedUp()
    {
        hud.SetObjective(
            "Objective: Repair the Power Node in Maintenance."
        );
    }

    private void OnPowerNodeCompleted()
    {
        hud.SetObjective(
            "Objective: Activate the Control Terminal."
        );
    }

    private void OnControlTerminalCompleted()
    {
        hud.SetObjective(
            "Objective: Reach the Exit."
        );
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

        hud.SetObjective("Mission Complete");

        hud.ShowFeedback(
            "Facility restored. Exit reached.",
            4f
        );

        Debug.Log("Vertical Slice Complete!");
    }
}