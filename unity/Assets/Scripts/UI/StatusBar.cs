using UnityEngine;
using TMPro;

namespace Themis.Unity.UI
{
    /// <summary>
    /// Status bar at top of screen showing system status.
    /// </summary>
    public class StatusBar : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI statusText;
        [SerializeField] private TextMeshProUGUI fpsText;
        [SerializeField] private TextMeshProUGUI connectionText;

        [Header("Configuration")]
        [SerializeField] private float fpsUpdateInterval = 0.5f;

        private float _fpsTimer;
        private int _frameCount;

        private void Start()
        {
            UpdateStatus("Initializing...");
        }

        private void Update()
        {
            // FPS counter
            _frameCount++;
            _fpsTimer += Time.unscaledDeltaTime;

            if (_fpsTimer >= fpsUpdateInterval)
            {
                float fps = _frameCount / _fpsTimer;
                if (fpsText != null)
                {
                    fpsText.text = $"FPS: {fps:F0}";
                }
                _frameCount = 0;
                _fpsTimer = 0;
            }
        }

        /// <summary>
        /// Update main status text.
        /// </summary>
        public void UpdateStatus(string status)
        {
            if (statusText != null)
            {
                statusText.text = status;
            }
        }

        /// <summary>
        /// Update connection status.
        /// </summary>
        public void UpdateConnection(bool connected)
        {
            if (connectionText != null)
            {
                connectionText.text = connected ? "Connected" : "Disconnected";
                connectionText.color = connected ? Color.green : Color.red;
            }
        }
    }
}
