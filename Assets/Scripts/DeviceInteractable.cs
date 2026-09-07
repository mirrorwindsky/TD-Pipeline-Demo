using System;
using UnityEngine;

public class DeviceInteractable : MonoBehaviour, IInteractable
{
    [SerializeField] private string displayName = "Device";

    [SerializeField] private string requiredItemId = "";
    [SerializeField] private bool consumeRequiredItem = true;

    [SerializeField] private int requiredInteractions = 1;
    [SerializeField] private bool deactivateOnComplete = false;

    [SerializeField] private DeviceInteractable requiredDevice;

    [SerializeField]
    private string blockedMessage = "Requirements not met.";

    [SerializeField]
    private string completionMessage = "Device completed.";

    [SerializeField] private string configId;
    [SerializeField] private InteractableConfigDatabase database;

    private InteractableConfig config;

    private void Start()
    {
        if (!database.TryGetConfig(configId, out config))
        {
            Debug.LogError(
                $"Config not found: {configId}",
                this
            );

            enabled = false;
            return;
        }

        displayName = config.displayName;
        requiredItemId = config.requiredItemId;
        requiredInteractions = config.requiredInteractions;
        deactivateOnComplete = config.deactivateOnComplete;

        if (!string.IsNullOrWhiteSpace(config.blockedMessage))
        {
            blockedMessage = config.blockedMessage;
        }

        if (!string.IsNullOrWhiteSpace(config.completionMessage))
        {
            completionMessage = config.completionMessage;
        }
    }

    public event Action Completed;

    // 当前操作进度
    private int interactionCount;

    // 入场条件是否已经满足
    private bool requirementSatisfied;

    // 整个设备是否已经完成
    private bool isCompleted;

    public string DisplayName => displayName;
    public bool IsCompleted => isCompleted;

    public void Interact(GameObject interactor)
    {
        PlayerHUD hud =
            interactor.GetComponent<PlayerHUD>();

        // 已经完成的设备不再重复执行
        if (isCompleted)
        {
            Debug.Log($"{displayName} is already complete.");

            hud?.ShowFeedback(
                $"{displayName} is already complete."
            );

            return;
        }

        // 检查前置设备
        if (requiredDevice != null &&
            !requiredDevice.IsCompleted)
        {
            Debug.Log(
                $"{displayName} requires " +
                $"{requiredDevice.DisplayName} to be completed."
            );

            hud?.ShowFeedback(blockedMessage);

            return;
        }

        // 第一次进入操作流程时检查物品条件
        if (!requirementSatisfied)
        {
            if (!string.IsNullOrWhiteSpace(requiredItemId))
            {
                PlayerInventory inventory =
                    interactor.GetComponent<PlayerInventory>();

                if (inventory == null)
                {
                    Debug.LogError(
                        $"Interactor has no PlayerInventory: " +
                        $"{interactor.name}",
                        this
                    );

                    return;
                }

                if (!inventory.HasItem(requiredItemId))
                {
                    Debug.Log(
                        $"{displayName} requires item: " +
                        $"{requiredItemId}"
                    );

                    hud?.ShowFeedback(blockedMessage);

                    return;
                }

                if (consumeRequiredItem)
                {
                    inventory.RemoveItem(requiredItemId);
                }
            }

            // 条件一旦满足，后续交互不再重复检查和消耗物品
            requirementSatisfied = true;
        }

        // 正常增加交互进度
        interactionCount++;

        Debug.Log(
            $"{displayName}: " +
            $"{interactionCount}/{requiredInteractions}"
        );

        hud?.ShowFeedback(
            $"{displayName}: " +
            $"{interactionCount}/{requiredInteractions}"
        );

        // 还没达到完成次数
        if (interactionCount < requiredInteractions)
            return;

        // 设备完成
        isCompleted = true;

        Debug.Log($"{displayName} completed.");

        hud?.ShowFeedback(completionMessage);

        Completed?.Invoke();

        if (deactivateOnComplete)
        {
            gameObject.SetActive(false);
        }
    }
}