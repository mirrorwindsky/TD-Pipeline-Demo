using System.Collections;
using TMPro;
using UnityEngine;

public class PlayerHUD : MonoBehaviour
{
    [SerializeField] private TMP_Text objectiveText;
    [SerializeField] private TMP_Text feedbackText;
    [SerializeField] private TMP_Text promptText;

    [Header("Optional presentation panels")]
    [SerializeField] private GameObject objectivePanel;
    [SerializeField] private GameObject feedbackPanel;
    [SerializeField] private GameObject promptPanel;
    [SerializeField] private GameObject missionCompletePanel;
    [SerializeField] private TMP_Text missionCompleteText;

    private Coroutine feedbackCoroutine;
    private bool missionCompleteShown;

    private void Awake()
    {
        missionCompleteShown = false;
        SetObjective("");
        feedbackText.text = "";
        SetPrompt("");
        SetPanelVisible(feedbackPanel, false);
        SetPanelVisible(missionCompletePanel, false);
        if (missionCompleteText != null)
            missionCompleteText.text = "";
    }

    public void SetObjective(string text)
    {
        // The V2 card has its own static label; the description still comes from config.
        const string prefix = "Objective: ";
        if (objectivePanel != null && text != null &&
            text.StartsWith(prefix, System.StringComparison.Ordinal))
        {
            text = text.Substring(prefix.Length);
        }

        objectiveText.text = text;
        SetPanelVisible(objectivePanel, !missionCompleteShown && !string.IsNullOrWhiteSpace(text));
    }

    public void SetPrompt(string text)
    {
        if (missionCompleteShown)
            text = "";
        else if (promptPanel != null && text == "Press E to interact")
            text = "<color=#9DD3DA><b>[E]</b></color>  Interact";

        promptText.text = text;
        SetPanelVisible(promptPanel, !string.IsNullOrWhiteSpace(text));
    }

    public void ShowMissionComplete()
    {
        if (missionCompletePanel == null || missionCompleteText == null)
            return;

        // Reuse the final config-driven objective instead of duplicating its content.
        missionCompleteText.text = objectiveText.text;
        missionCompleteShown = true;
        SetPanelVisible(objectivePanel, false);
        SetPanelVisible(missionCompletePanel, true);
        SetPrompt("");
    }

    public void ShowFeedback(string text, float duration = 2f)
    {
        feedbackText.text = text;
        SetPanelVisible(feedbackPanel, !string.IsNullOrWhiteSpace(text));

        if (feedbackCoroutine != null)
        {
            StopCoroutine(feedbackCoroutine);
        }

        feedbackCoroutine = StartCoroutine(
            ClearFeedbackAfter(duration)
        );
    }

    private IEnumerator ClearFeedbackAfter(float duration)
    {
        yield return new WaitForSeconds(duration);

        feedbackText.text = "";
        SetPanelVisible(feedbackPanel, false);
        feedbackCoroutine = null;
    }

    private static void SetPanelVisible(GameObject panel, bool visible)
    {
        if (panel != null && panel.activeSelf != visible)
            panel.SetActive(visible);
    }
}
