using UnityEngine;

[DisallowMultipleComponent]
public class CompletionVisualFeedback : MonoBehaviour
{
    [SerializeField] private DeviceInteractable completionSource;
    [SerializeField] private Renderer[] targetRenderers = new Renderer[0];
    [SerializeField] private Material idleMaterial;
    [SerializeField] private Material completedMaterial;

    private DeviceInteractable subscribedSource;

    private void OnEnable()
    {
        subscribedSource = completionSource;
        if (subscribedSource != null)
            subscribedSource.Completed += OnCompleted;

        // Also restore the right appearance if enabled after completion.
        ApplyState(subscribedSource != null && subscribedSource.IsCompleted);
    }

    private void OnDisable()
    {
        if (subscribedSource != null)
            subscribedSource.Completed -= OnCompleted;

        subscribedSource = null;
        ApplyState(false);
    }

    private void OnCompleted()
    {
        ApplyState(true);
    }

    private void ApplyState(bool completed)
    {
        Material material = completed ? completedMaterial : idleMaterial;
        if (material == null || targetRenderers == null)
            return;

        foreach (Renderer targetRenderer in targetRenderers)
        {
            if (targetRenderer == null)
                continue;

            // Swap only this renderer's reference; never edit a shared asset
            // or create runtime material instances that need cleanup.
            targetRenderer.sharedMaterial = material;
        }
    }
}
