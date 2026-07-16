using UnityEngine;
using TMPro;

namespace Themis.Unity.UI
{
    public class OccupancyDisplay : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshPro textMesh;
        [SerializeField] private GameObject displayPanel;

        [Header("Configuration")]
        [SerializeField] private int carId;

        private void Start()
        {
            if (textMesh == null)
                textMesh = GetComponentInChildren<TextMeshPro>();

            UpdateDisplay(0, "GREEN");
        }

        public void UpdateDisplay(float occupancyPct, string densityIndicator)
        {
            if (textMesh != null)
            {
                textMesh.text = $"{occupancyPct:F0}%";
                textMesh.color = GetDensityColor(densityIndicator);
            }

            if (displayPanel != null)
            {
                Renderer panelRenderer = displayPanel.GetComponent<Renderer>();
                if (panelRenderer != null)
                {
                    panelRenderer.material.color = GetDensityColor(densityIndicator) * 0.5f;
                }
            }
        }

        private Color GetDensityColor(string densityIndicator)
        {
            switch (densityIndicator)
            {
                case "GREEN": return new Color(0.15f, 0.68f, 0.38f);
                case "YELLOW": return new Color(1f, 0.75f, 0.0f);
                case "RED": return new Color(0.95f, 0.25f, 0.05f);
                default: return Color.gray;
            }
        }
    }
}
