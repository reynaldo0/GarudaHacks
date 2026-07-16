using UnityEngine;

namespace Themis.Unity.Indicators
{
    /// <summary>
    /// LED indicator on train car doors.
    /// Shows occupancy status with color.
    /// </summary>
    public class LEDIndicator : MonoBehaviour
    {
        [Header("LED Configuration")]
        [SerializeField] private Renderer ledRenderer;
        [SerializeField] private string state = "OFF";

        [Header("Colors")]
        [SerializeField] private Color greenColor = Color.green;
        [SerializeField] private Color yellowColor = Color.yellow;
        [SerializeField] private Color redColor = Color.red;
        [SerializeField] private Color offColor = Color.black;

        private Material _material;

        private void Start()
        {
            if (ledRenderer == null)
                ledRenderer = GetComponent<Renderer>();

            if (ledRenderer != null)
                _material = ledRenderer.material;

            SetState("OFF");
        }

        /// <summary>
        /// Set LED state.
        /// </summary>
        public void SetState(string newState)
        {
            state = newState;
            UpdateVisual();
        }

        private void UpdateVisual()
        {
            if (_material == null) return;

            Color targetColor;
            switch (state)
            {
                case "GREEN":
                    targetColor = greenColor;
                    break;
                case "YELLOW":
                    targetColor = yellowColor;
                    break;
                case "RED":
                    targetColor = redColor;
                    break;
                case "RED_BLINK":
                    targetColor = redColor;
                    StartCoroutine(BlinkCoroutine());
                    return;
                default:
                    targetColor = offColor;
                    break;
            }

            _material.color = targetColor;
            _material.SetColor("_EmissionColor", targetColor * 2f);
        }

        private System.Collections.IEnumerator BlinkCoroutine()
        {
            for (int i = 0; i < 10; i++)
            {
                _material.color = redColor;
                yield return new WaitForSeconds(0.3f);
                _material.color = offColor;
                yield return new WaitForSeconds(0.3f);
            }
        }
    }
}
