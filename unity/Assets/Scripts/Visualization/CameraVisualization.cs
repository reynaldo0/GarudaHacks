using UnityEngine;

namespace Themis.Unity.Visualization
{
    /// <summary>
    /// Camera Visualization for displaying virtual CCTV feed.
    /// Shows camera view in a UI panel or 3D screen.
    /// </summary>
    public class CameraVisualization : MonoBehaviour
    {
        [Header("Camera Settings")]
        [SerializeField] private Camera sourceCamera;
        [SerializeField] private RenderTexture renderTexture;
        [SerializeField] private int width = 640;
        [SerializeField] private int height = 480;

        [Header("Display Settings")]
        [SerializeField] private Renderer displayRenderer;
        [SerializeField] private bool showOverlay = true;
        [SerializeField] private string cameraName = "CAM-01";

        private Material _displayMaterial;
        private bool _isStreaming = false;

        private void Awake()
        {
            if (displayRenderer)
            {
                _displayMaterial = displayRenderer.material;
            }

            // Create render texture if not assigned
            if (renderTexture == null)
            {
                renderTexture = new RenderTexture(width, height, 16);
                renderTexture.Create();
            }

            // Assign to camera
            if (sourceCamera)
            {
                sourceCamera.targetTexture = renderTexture;
            }

            // Assign to display
            if (_displayMaterial)
            {
                _displayMaterial.mainTexture = renderTexture;
            }
        }

        private void Update()
        {
            if (_isStreaming && sourceCamera)
            {
                // Camera is already rendering to texture
                // This loop ensures continuous rendering
            }
        }

        /// <summary>
        /// Start streaming camera feed.
        /// </summary>
        public void StartStreaming()
        {
            _isStreaming = true;
            if (sourceCamera)
            {
                sourceCamera.enabled = true;
            }
            Debug.Log($"[Camera] Streaming started: {cameraName}");
        }

        /// <summary>
        /// Stop streaming camera feed.
        /// </summary>
        public void StopStreaming()
        {
            _isStreaming = false;
            if (sourceCamera)
            {
                sourceCamera.enabled = false;
            }
            Debug.Log($"[Camera] Streaming stopped: {cameraName}");
        }

        /// <summary>
        /// Get current frame as Texture2D.
        /// </summary>
        public Texture2D CaptureFrame()
        {
            if (renderTexture == null) return null;

            RenderTexture.active = renderTexture;
            Texture2D frame = new Texture2D(width, height, TextureFormat.RGB24, false);
            frame.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            frame.Apply();
            RenderTexture.active = null;

            return frame;
        }

        /// <summary>
        /// Set camera name overlay.
        /// </summary>
        public void SetCameraName(string name)
        {
            cameraName = name;
            Debug.Log($"[Camera] Name set to: {name}");
        }

        /// <summary>
        /// Toggle overlay display.
        /// </summary>
        public void ToggleOverlay()
        {
            showOverlay = !showOverlay;
            Debug.Log($"[Camera] Overlay toggled: {showOverlay}");
        }

        private void OnDestroy()
        {
            if (renderTexture != null)
            {
                renderTexture.Release();
            }
        }
    }
}
