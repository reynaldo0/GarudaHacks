using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace Themis.Unity.Camera
{
    public class CameraSimulator : MonoBehaviour
    {
        [Header("Camera Settings")]
        [SerializeField] private UnityEngine.Camera captureCamera;
        [SerializeField] private string cameraId = "car01_cam01";
        [SerializeField] private string trainId = "SF10-001";
        [SerializeField] private int captureWidth = 640;
        [SerializeField] private int captureHeight = 640;
        [SerializeField] private float captureInterval = 5f;
        [SerializeField] private string apiUrl = "http://localhost:8005";

        [Header("Fisheye Settings")]
        [SerializeField] private float fisheyeFOV = 170f;
        [SerializeField] private bool isFisheye = true;

        [Header("Status")]
        [SerializeField] private bool isCapturing = false;
        [SerializeField] private int frameCount = 0;

        [Header("References")]
        [SerializeField] private Network.ApiClient apiClient;

        private RenderTexture _renderTexture;
        private Texture2D _texture2D;
        private Coroutine _captureCoroutine;

        public bool IsCapturing => isCapturing;
        public int FrameCount => frameCount;
        public string CameraId => cameraId;
        public bool IsFisheye => isFisheye;

        private void Start()
        {
            if (captureCamera == null)
                captureCamera = GetComponent<UnityEngine.Camera>();

            if (captureCamera == null)
            {
                Debug.LogError("[CameraSim] No camera found. Attach to a Camera object or assign one.");
                return;
            }

            if (isFisheye)
                captureCamera.fieldOfView = fisheyeFOV;

            _renderTexture = new RenderTexture(captureWidth, captureHeight, 24, RenderTextureFormat.ARGB32);
            _renderTexture.Create();
            captureCamera.targetTexture = _renderTexture;

            _texture2D = new Texture2D(captureWidth, captureHeight, TextureFormat.RGB24, false);

            if (apiClient == null)
                apiClient = FindObjectOfType<Network.ApiClient>();

            Debug.Log($"[CameraSim] Initialized: {cameraId} ({captureWidth}x{captureHeight}) fisheye={isFisheye} FOV={fisheyeFOV}");
        }

        public void StartCapture()
        {
            if (isCapturing) return;

            if (captureCamera == null || _renderTexture == null)
            {
                Debug.LogError("[CameraSim] Cannot start capture - camera not ready");
                return;
            }

            isCapturing = true;
            _captureCoroutine = StartCoroutine(CaptureLoop());
            Debug.Log($"[CameraSim] Capture started: {cameraId}");
        }

        public void StopCapture()
        {
            isCapturing = false;
            if (_captureCoroutine != null)
            {
                StopCoroutine(_captureCoroutine);
                _captureCoroutine = null;
            }
            Debug.Log($"[CameraSim] Capture stopped: {cameraId}");
        }

        public void SetTrainId(string id)
        {
            trainId = id;
        }

        public void SetCameraId(string id)
        {
            cameraId = id;
        }

        public void SetApiClient(Network.ApiClient client)
        {
            apiClient = client;
        }

        public void SetFisheye(bool enabled, float fov = 170f)
        {
            isFisheye = enabled;
            fisheyeFOV = fov;
            if (captureCamera != null && isFisheye)
                captureCamera.fieldOfView = fov;
        }

        public byte[] CaptureFrame()
        {
            if (captureCamera == null || _renderTexture == null)
                return null;

            captureCamera.Render();

            RenderTexture.active = _renderTexture;
            _texture2D.ReadPixels(new Rect(0, 0, captureWidth, captureHeight), 0, 0);
            _texture2D.Apply();
            RenderTexture.active = null;

            byte[] jpegData = _texture2D.EncodeToJPG(85);
            frameCount++;

            return jpegData;
        }

        public void CaptureAndUpload()
        {
            byte[] frameData = CaptureFrame();
            if (frameData == null)
            {
                Debug.LogWarning("[CameraSim] CaptureFrame returned null");
                return;
            }

            if (apiClient != null)
            {
                apiClient.UploadFrame(frameData, cameraId, (success) =>
                {
                    if (success)
                        Debug.Log($"[CameraSim] Frame {frameCount} uploaded: {cameraId}");
                    else
                        Debug.LogWarning($"[CameraSim] Frame {frameCount} upload failed: {cameraId}");
                });
            }
            else
            {
                StartCoroutine(UploadFrameDirect(frameData));
            }
        }

        private IEnumerator CaptureLoop()
        {
            while (isCapturing)
            {
                yield return new WaitForSeconds(captureInterval);
                CaptureAndUpload();
            }
        }

        private IEnumerator UploadFrameDirect(byte[] frameData)
        {
            string baseUrl = apiClient != null ? apiClient.BaseUrl : apiUrl;
            string url = $"{baseUrl}/api/v1/frame?camera_id={cameraId}&train_id={trainId}";

            List<IMultipartFormSection> form = new List<IMultipartFormSection>
            {
                new MultipartFormFileSection("file", frameData, "frame.jpg", "image/jpeg")
            };

            using (UnityWebRequest request = UnityWebRequest.Post(url, form))
            {
                request.timeout = 15;
                request.SetRequestHeader("Accept", "application/json");
                request.SetRequestHeader("X-API-Key", "themis-unity-key-2026");
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"[CameraSim] Direct upload OK: {cameraId} frame {frameCount}");
                }
                else
                {
                    Debug.LogWarning($"[CameraSim] Direct upload failed: {request.error}");
                }
            }
        }

        private void OnDestroy()
        {
            StopCapture();

            if (_renderTexture != null)
            {
                _renderTexture.Release();
                Destroy(_renderTexture);
            }

            if (_texture2D != null)
            {
                Destroy(_texture2D);
            }
        }
    }
}
