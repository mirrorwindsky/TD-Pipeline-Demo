using System.Collections;
using TMPro;
using UnityEngine;

public class PlayerHUD : MonoBehaviour
{
    [SerializeField] private TMP_Text objectiveText;
    [SerializeField] private TMP_Text feedbackText;
    [SerializeField] private TMP_Text promptText;

    private Coroutine feedbackCoroutine;

    private void Awake()
    {
        objectiveText.text = "";
        feedbackText.text = "";
        promptText.text = "";
    }

    public void SetObjective(string text)
    {
        objectiveText.text = text;
    }

    public void SetPrompt(string text)
    {
        promptText.text = text;
    }

    public void ShowFeedback(string text, float duration = 2f)
    {
        feedbackText.text = text;

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
        feedbackCoroutine = null;
    }
}