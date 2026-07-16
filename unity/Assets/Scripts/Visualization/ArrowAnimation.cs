using System.Collections;
using UnityEngine;

namespace Themis.Unity.Visualization
{
    /// <summary>
    /// Arrow Animation for recommendation visualization.
    /// Shows animated arrow pointing to recommended car.
    /// </summary>
    public class ArrowAnimation : MonoBehaviour
    {
        [Header("Arrow Settings")]
        [SerializeField] private float animationSpeed = 2f;
        [SerializeField] private float bounceHeight = 0.3f;
        [SerializeField] private Color activeColor = Color.green;
        [SerializeField] private Color inactiveColor = Color.gray;

        private bool _isActive = false;
        private Vector3 _startPosition;
        private Renderer _renderer;
        private Material _material;

        private void Awake()
        {
            _startPosition = transform.localPosition;
            _renderer = GetComponent<Renderer>();
            if (_renderer)
            {
                _material = _renderer.material;
            }
        }

        private void Update()
        {
            if (_isActive)
            {
                // Bounce animation
                float newY = _startPosition.y + Mathf.Sin(Time.time * animationSpeed) * bounceHeight;
                transform.localPosition = new Vector3(
                    _startPosition.x,
                    newY,
                    _startPosition.z
                );
            }
        }

        /// <summary>
        /// Activate arrow animation pointing to target car.
        /// </summary>
        public void Activate(Vector3 targetPosition)
        {
            _isActive = true;
            transform.position = targetPosition + Vector3.up * 2f;
            gameObject.SetActive(true);

            if (_material)
            {
                _material.color = activeColor;
            }

            Debug.Log($"[Arrow] Activated at {targetPosition}");
        }

        /// <summary>
        /// Deactivate arrow animation.
        /// </summary>
        public void Deactivate()
        {
            _isActive = false;
            transform.localPosition = _startPosition;
            gameObject.SetActive(false);

            if (_material)
            {
                _material.color = inactiveColor;
            }

            Debug.Log("[Arrow] Deactivated");
        }

        /// <summary>
        /// Set arrow color.
        /// </summary>
        public void SetColor(Color color)
        {
            if (_material)
            {
                _material.color = color;
            }
        }
    }
}
