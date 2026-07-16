using UnityEngine;

namespace Themis.Unity.Visualization
{
    /// <summary>
    /// Recommendation Highlight for visualizing recommended car.
    /// Highlights the target car with glow effect and color change.
    /// </summary>
    public class RecommendationHighlight : MonoBehaviour
    {
        [Header("Highlight Settings")]
        [SerializeField] private float glowIntensity = 1.5f;
        [SerializeField] private float pulseSpeed = 2f;
        [SerializeField] private Color highlightColor = Color.green;
        [SerializeField] private Color sourceColor = Color.red;

        private bool _isHighlighted = false;
        private bool _isPulsing = false;
        private Renderer _renderer;
        private Material _material;
        private Color _originalColor;

        private void Awake()
        {
            _renderer = GetComponent<Renderer>();
            if (_renderer)
            {
                _material = _renderer.material;
                _originalColor = _material.color;
            }
        }

        private void Update()
        {
            if (_isPulsing && _material)
            {
                // Pulse effect
                float pulse = (Mathf.Sin(Time.time * pulseSpeed) + 1f) / 2f;
                _material.color = Color.Lerp(_originalColor, highlightColor, pulse * glowIntensity);
            }
        }

        /// <summary>
        /// Highlight as recommended target car.
        /// </summary>
        public void HighlightAsTarget()
        {
            _isHighlighted = true;
            _isPulsing = true;

            if (_material)
            {
                _material.color = highlightColor;
            }

            Debug.Log($"[Highlight] Target car highlighted: {gameObject.name}");
        }

        /// <summary>
        /// Highlight as source car (where passengers should move from).
        /// </summary>
        public void HighlightAsSource()
        {
            _isHighlighted = true;
            _isPulsing = false;

            if (_material)
            {
                _material.color = sourceColor;
            }

            Debug.Log($"[Highlight] Source car highlighted: {gameObject.name}");
        }

        /// <summary>
        /// Remove highlight.
        /// </summary>
        public void RemoveHighlight()
        {
            _isHighlighted = false;
            _isPulsing = false;

            if (_material)
            {
                _material.color = _originalColor;
            }

            Debug.Log($"[Highlight] Highlight removed: {gameObject.name}");
        }

        /// <summary>
        /// Set custom highlight color.
        /// </summary>
        public void SetHighlightColor(Color color)
        {
            highlightColor = color;
            if (_isHighlighted && _material)
            {
                _material.color = color;
            }
        }
    }
}
