using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace Themis.Unity.Network
{
    public class ApiClient : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string baseUrl = "http://localhost:8005";
        [SerializeField] private float timeout = 10f;
        [SerializeField] private string apiKey = "themis-unity-key-2026";

        public event Action<string> OnStateReceived;
        public event Action<string> OnError;

        private string _trainId = "SF10-001";

        public string BaseUrl => baseUrl;
        public string TrainId => _trainId;

        public void SetTrainId(string trainId)
        {
            _trainId = trainId;
        }

        public void GetState(Action<string> callback)
        {
            StartCoroutine(GetCoroutine($"/api/v1/state?train_id={_trainId}", callback));
        }

        public void GetOccupancy(Action<string> callback)
        {
            StartCoroutine(GetCoroutine($"/api/v1/occupancy?train_id={_trainId}", callback));
        }

        public void GetPipelineState(string carId, Action<string> callback)
        {
            StartCoroutine(GetCoroutine($"/api/v1/state/{carId}?train_id={_trainId}", callback));
        }

        public void GetRecommendation(Action<string> callback)
        {
            StartCoroutine(GetCoroutine($"/api/v1/recommendation?train_id={_trainId}", callback));
        }

        public void GetWarnings(Action<string> callback)
        {
            StartCoroutine(GetCoroutine($"/api/v1/history/warnings?train_id={_trainId}", callback));
        }

        public void UploadFrame(byte[] frameData, string cameraId, Action<bool> callback)
        {
            StartCoroutine(UploadFrameCoroutine(frameData, cameraId, callback));
        }

        public void UploadMultipleFrames(byte[][] frameDataArray, string[] cameraIds, Action<bool> callback)
        {
            StartCoroutine(UploadMultipleFramesCoroutine(frameDataArray, cameraIds, callback));
        }

        public void LoadScenario(string scenarioName, Action<bool> callback)
        {
            StartCoroutine(PostCoroutine($"/api/v1/simulation/scenario/{scenarioName}", "", callback));
        }

        public void ResetSimulation(Action<bool> callback)
        {
            StartCoroutine(PostCoroutine("/api/v1/simulation/reset", "", callback));
        }

        public void HealthCheck(Action<string> callback)
        {
            StartCoroutine(GetCoroutine("/health", callback));
        }

        private IEnumerator UploadFrameCoroutine(byte[] frameData, string cameraId, Action<bool> callback)
        {
            string url = $"{baseUrl}/api/v1/frame?camera_id={cameraId}&train_id={_trainId}";

            List<IMultipartFormSection> form = new List<IMultipartFormSection>
            {
                new MultipartFormFileSection("file", frameData, "frame.jpg", "image/jpeg")
            };

            using (UnityWebRequest request = UnityWebRequest.Post(url, form))
            {
                request.timeout = (int)timeout;
                request.SetRequestHeader("Accept", "application/json");
                request.SetRequestHeader("X-API-Key", apiKey);
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"[API] Frame uploaded: {cameraId} ({frameData.Length} bytes)");
                    callback?.Invoke(true);
                }
                else
                {
                    Debug.LogError($"[API] Frame upload failed: {request.error}");
                    OnError?.Invoke(request.error);
                    callback?.Invoke(false);
                }
            }
        }

        private IEnumerator UploadMultipleFramesCoroutine(byte[][] frameDataArray, string[] cameraIds, Action<bool> callback)
        {
            bool allSuccess = true;

            for (int i = 0; i < frameDataArray.Length; i++)
            {
                bool frameSuccess = false;
                yield return UploadFrameCoroutine(frameDataArray[i], cameraIds[i], (success) =>
                {
                    frameSuccess = success;
                    if (!success) allSuccess = false;
                });

                yield return new WaitForSeconds(0.1f);
            }

            callback?.Invoke(allSuccess);
        }

        private IEnumerator GetCoroutine(string path, Action<string> callback)
        {
            string url = $"{baseUrl}{path}";

            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.timeout = (int)timeout;
                request.SetRequestHeader("Accept", "application/json");
                request.SetRequestHeader("X-API-Key", apiKey);
                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    string text = request.downloadHandler.text;
                    callback?.Invoke(text);
                }
                else
                {
                    Debug.LogWarning($"[API] GET {path} failed: {request.error}");
                    OnError?.Invoke(request.error);
                    callback?.Invoke(null);
                }
            }
        }

        private IEnumerator PostCoroutine(string path, string json, Action<bool> callback)
        {
            string url = $"{baseUrl}{path}";

            byte[] bodyRaw = string.IsNullOrEmpty(json)
                ? null
                : System.Text.Encoding.UTF8.GetBytes(json);

            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                if (bodyRaw != null)
                {
                    request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                    request.SetRequestHeader("Content-Type", "application/json");
                }
                else
                {
                    request.SetRequestHeader("Content-Type", "application/json");
                }

                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Accept", "application/json");
                request.SetRequestHeader("X-API-Key", apiKey);
                request.timeout = (int)timeout;

                yield return request.SendWebRequest();

                if (request.result == UnityWebRequest.Result.Success)
                {
                    Debug.Log($"[API] POST {path} OK");
                    callback?.Invoke(true);
                }
                else
                {
                    Debug.LogError($"[API] POST {path} failed: {request.error}");
                    OnError?.Invoke(request.error);
                    callback?.Invoke(false);
                }
            }
        }
    }
}
