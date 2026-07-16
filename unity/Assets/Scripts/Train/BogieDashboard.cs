using UnityEngine;
using TMPro;

namespace Themis.Unity.Train
{
    public class BogieDashboard : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshPro textMesh;

        [Header("Display Values")]
        [SerializeField] private float calesScore = 0f;
        [SerializeField] private float healthIndex = 100f;
        [SerializeField] private float damageMultiplier = 1f;
        [SerializeField] private int inspectionPriority = 0;
        [SerializeField] private string recommendedAction = "CONTINUE_MONITORING";

        public float CalesScore => calesScore;
        public float HealthIndex => healthIndex;
        public int InspectionPriority => inspectionPriority;

        private void Start()
        {
            if (textMesh == null)
                textMesh = GetComponentInChildren<TextMeshPro>();

            UpdateDashboard(0f, 100f, 1f, 0, "CONTINUE_MONITORING");
        }

        public void UpdateDashboard(
            float newCalesScore,
            float newHealthIndex,
            float newDamageMultiplier,
            int newInspectionPriority,
            string newRecommendedAction)
        {
            calesScore = newCalesScore;
            healthIndex = newHealthIndex;
            damageMultiplier = newDamageMultiplier;
            inspectionPriority = newInspectionPriority;
            recommendedAction = newRecommendedAction;

            if (textMesh != null)
            {
                string priorityLabel = inspectionPriority switch
                {
                    1 => "CRITICAL",
                    2 => "HIGH",
                    3 => "MEDIUM",
                    _ => "LOW"
                };

                textMesh.text =
                    $"CALES: {calesScore:F2}\n" +
                    $"Health: {healthIndex:F1}%\n" +
                    $"Dmg: x{damageMultiplier:F2}\n" +
                    $"Priority: {priorityLabel}";

                textMesh.color = GetPriorityColor(inspectionPriority);
            }
        }

        private Color GetPriorityColor(int priority)
        {
            return priority switch
            {
                1 => Color.red,
                2 => new Color(1f, 0.6f, 0f),
                3 => Color.yellow,
                _ => Color.green
            };
        }
    }
}
