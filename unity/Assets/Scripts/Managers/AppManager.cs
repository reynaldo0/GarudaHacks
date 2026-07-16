using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Themis.Unity.Train;
using Themis.Unity.Camera;

namespace Themis.Unity.Managers
{
    public class AppManager : MonoBehaviour
    {
        public static AppManager Instance { get; private set; }

        [Header("References")]
        [SerializeField] private Network.WebSocketClient wsClient;
        [SerializeField] private Network.ApiClient apiClient;
        [SerializeField] private TrainController trainController;

        [Header("Configuration")]
        [SerializeField] private string trainId = "SF10-001";
        [SerializeField] private float pollInterval = 3f;
        [SerializeField] private bool autoPoll = true;

        public Network.WebSocketClient WSClient => wsClient;
        public Network.ApiClient ApiClient => apiClient;
        public TrainController TrainCtrl => trainController;
        public string TrainId => trainId;

        public event Action<string> OnTrainIdChanged;

        private Coroutine _pollCoroutine;
        private bool _initialized = false;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        private void Start()
        {
            Debug.Log("[AppManager] PROJECT THEMIS V6 Unity Digital Twin starting...");
            StartCoroutine(InitializeSequence());
        }

        private void Update()
        {
            Network.UnityMainThreadDispatcher.ProcessQueue();
        }

        private IEnumerator InitializeSequence()
        {
            yield return new WaitForSeconds(0.1f);

            if (apiClient == null)
                apiClient = FindObjectOfType<Network.ApiClient>();
            if (wsClient == null)
                wsClient = FindObjectOfType<Network.WebSocketClient>();
            if (trainController == null)
                trainController = FindObjectOfType<TrainController>();

            if (apiClient != null)
                apiClient.SetTrainId(trainId);

            if (trainController != null)
                trainController.SetTrainId(trainId);

            if (wsClient != null)
            {
                wsClient.OnConnected += OnWSConnected;
                wsClient.OnDisconnected += OnWSDisconnected;
                wsClient.OnMessageReceived += OnWSMessage;
            }

            if (apiClient != null)
            {
                apiClient.OnError += OnApiError;
            }

            _initialized = true;
            Debug.Log("[AppManager] Initialization complete");

            StartCameraCaptureForAllCars();

            if (autoPoll)
            {
                StartPolling();
            }

            PollState();
        }

        public void SetTrainId(string newTrainId)
        {
            trainId = newTrainId;

            if (apiClient != null)
                apiClient.SetTrainId(newTrainId);

            if (trainController != null)
                trainController.SetTrainId(newTrainId);

            OnTrainIdChanged?.Invoke(newTrainId);
        }

        public void StartCameraCaptureForAllCars()
        {
            if (trainController == null) return;

            foreach (var car in trainController.Cars)
            {
                car.CreateCeilingFisheyeCameras(apiClient);
                car.StartCameraCapture();
            }

            Debug.Log("[AppManager] All car ceiling fisheye cameras started");
        }

        public void StartPolling()
        {
            if (_pollCoroutine != null) StopCoroutine(_pollCoroutine);
            _pollCoroutine = StartCoroutine(PollLoop());
            Debug.Log("[AppManager] Polling started");
        }

        public void StopPolling()
        {
            if (_pollCoroutine != null)
            {
                StopCoroutine(_pollCoroutine);
                _pollCoroutine = null;
            }
        }

        private IEnumerator PollLoop()
        {
            while (true)
            {
                yield return new WaitForSeconds(pollInterval);
                PollState();
            }
        }

        public void PollState()
        {
            if (apiClient == null) return;

            apiClient.GetState((json) =>
            {
                if (string.IsNullOrEmpty(json)) return;
                ParseAndApplyState(json);
            });
        }

        private void ParseAndApplyState(string json)
        {
            if (trainController == null) return;

            try
            {
                string type = ExtractString(json, "type");

                if (type == "pipeline_state")
                {
                    HandlePipelineState(json);
                    return;
                }

                if (type == "occupancy_updated")
                {
                    HandleOccupancyUpdate(json);
                    return;
                }

                if (type == "recommendation_changed")
                {
                    HandleRecommendationUpdate(json);
                    return;
                }

                int carsIdx = json.IndexOf("\"cars\"");
                if (carsIdx < 0)
                {
                    int occIdx = json.IndexOf("\"occupancy_ratio\"");
                    if (occIdx >= 0)
                    {
                        HandleSinglePipelineState(json);
                    }
                    return;
                }

                int bracketStart = json.IndexOf('[', carsIdx);
                int bracketEnd = json.IndexOf(']', bracketStart);
                if (bracketStart < 0 || bracketEnd < 0) return;

                string carsArray = json.Substring(bracketStart + 1, bracketEnd - bracketStart - 1);

                List<TrainController.PipelineStateData> stateList = new List<TrainController.PipelineStateData>();

                int searchPos = 0;
                while (searchPos < carsArray.Length)
                {
                    int objStart = carsArray.IndexOf('{', searchPos);
                    if (objStart < 0) break;

                    int objEnd = FindMatchingBrace(carsArray, objStart);
                    if (objEnd < 0) break;

                    string carObj = carsArray.Substring(objStart, objEnd - objStart + 1);
                    searchPos = objEnd + 1;

                    TrainController.PipelineStateData state = ParsePipelineStateData(carObj);
                    if (state.carId > 0)
                        stateList.Add(state);
                }

                if (stateList.Count > 0)
                {
                    trainController.UpdateAllCars(stateList.ToArray());
                }

                string recTarget = ExtractString(json, "recommended_target");
                int fromCar = ExtractInt(json, "from_car_id");
                int toCar = ExtractInt(json, "to_car_id");

                if (fromCar > 0 && toCar > 0)
                {
                    trainController.HighlightRecommendedCar(fromCar, toCar);
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[AppManager] Parse error: {e.Message}");
            }
        }

        private void HandlePipelineState(string json)
        {
            try
            {
                string carIdStr = ExtractString(json, "car_id");
                if (string.IsNullOrEmpty(carIdStr)) return;

                string numericId = System.Text.RegularExpressions.Regex.Replace(carIdStr, "[^0-9]", "");
                if (!int.TryParse(numericId, out int carId)) return;

                TrainController.PipelineStateData state = ParsePipelineStateData(json);
                state.carId = carId;
                trainController.ApplyPipelineStateToCar(state);

                Debug.Log($"[AppManager] PipelineState: Car {carId} occ={state.occupancyRatio:F2} density={state.densityIndicator} door={state.doorAction}");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[AppManager] PipelineState parse error: {e.Message}");
            }
        }

        private void HandleSinglePipelineState(string json)
        {
            try
            {
                string carIdStr = ExtractString(json, "car_id");
                if (string.IsNullOrEmpty(carIdStr))
                {
                    int cid = ExtractInt(json, "car_id");
                    if (cid > 0)
                    {
                        TrainController.PipelineStateData state = ParsePipelineStateData(json);
                        state.carId = cid;
                        trainController.ApplyPipelineStateToCar(state);
                    }
                    return;
                }

                string numericId = System.Text.RegularExpressions.Regex.Replace(carIdStr, "[^0-9]", "");
                if (!int.TryParse(numericId, out int carId)) return;

                TrainController.PipelineStateData singleState = ParsePipelineStateData(json);
                singleState.carId = carId;
                trainController.ApplyPipelineStateToCar(singleState);
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[AppManager] Single state parse error: {e.Message}");
            }
        }

        private void HandleOccupancyUpdate(string json)
        {
            if (trainController == null) return;

            int carId = ExtractInt(json, "car_id");
            float occupancyRatio = ExtractFloat(json, "occupancy_ratio");
            string densityIndicator = ExtractString(json, "density_indicator");

            if (string.IsNullOrEmpty(densityIndicator))
            {
                string status = ExtractString(json, "status");
                if (!string.IsNullOrEmpty(status))
                    densityIndicator = MapOldStatus(status);
                else
                    densityIndicator = "GREEN";
            }

            if (carId > 0)
            {
                trainController.UpdateCarSpatialOccupancy(carId, occupancyRatio, densityIndicator);
                Debug.Log($"[AppManager] Occupancy updated: Car {carId} = {occupancyRatio:F2} [{densityIndicator}]");
            }
        }

        private void HandleRecommendationUpdate(string json)
        {
            if (trainController == null) return;

            int recIdx = json.IndexOf("\"recommendation\"");
            if (recIdx < 0)
            {
                int fromCar = ExtractInt(json, "from_car_id");
                int toCar = ExtractInt(json, "to_car_id");
                if (fromCar > 0 && toCar > 0)
                {
                    trainController.HighlightRecommendedCar(fromCar, toCar);
                    Debug.Log($"[AppManager] Recommendation: Car {fromCar} -> Car {toCar}");
                }
                return;
            }

            int braceStart = json.IndexOf('{', recIdx);
            if (braceStart < 0) return;

            string sub = json.Substring(braceStart);
            int fromCar = ExtractInt(sub, "from_car_id");
            int toCar = ExtractInt(sub, "to_car_id");

            if (fromCar > 0 && toCar > 0)
            {
                trainController.HighlightRecommendedCar(fromCar, toCar);
                Debug.Log($"[AppManager] Recommendation: Car {fromCar} -> Car {toCar}");
            }
        }

        private TrainController.PipelineStateData ParsePipelineStateData(string json)
        {
            var state = new TrainController.PipelineStateData();

            state.occupancyRatio = ExtractFloat(json, "occupancy_ratio");
            state.freeSpaceRatio = ExtractFloat(json, "free_space_ratio");
            state.spatialOccupancyScore = ExtractFloat(json, "spatial_occupancy_score");
            state.calesScore = ExtractFloat(json, "cales_score");
            state.healthIndex = ExtractFloat(json, "health_index");
            state.damageMultiplier = ExtractFloat(json, "damage_multiplier");
            state.inspectionPriority = ExtractInt(json, "inspection_priority");

            string density = ExtractString(json, "density_indicator");
            state.densityIndicator = string.IsNullOrEmpty(density) ? "GREEN" : density;

            string doorAction = ExtractString(json, "door_action");
            state.doorAction = string.IsNullOrEmpty(doorAction) ? "CLOSE" : doorAction;

            state.recommendedTarget = ExtractString(json, "recommended_target");
            state.announcement = ExtractString(json, "announcement");
            state.recommendedAction = ExtractString(json, "recommended_action");

            if (string.IsNullOrEmpty(state.recommendedAction))
                state.recommendedAction = "CONTINUE_MONITORING";

            return state;
        }

        private string MapOldStatus(string status)
        {
            switch (status)
            {
                case "LOW":
                case "NORMAL":
                    return "GREEN";
                case "HIGH":
                    return "YELLOW";
                case "FULL":
                case "OVERCAPACITY":
                    return "RED";
                default:
                    return "GREEN";
            }
        }

        private int ExtractInt(string json, string key)
        {
            string search = $"\"{key}\"";
            int keyIdx = json.IndexOf(search);
            if (keyIdx < 0) return 0;

            int colonIdx = json.IndexOf(':', keyIdx + search.Length);
            if (colonIdx < 0) return 0;

            int start = colonIdx + 1;
            while (start < json.Length && (json[start] == ' ' || json[start] == '\t'))
                start++;

            int end = start;
            if (end < json.Length && json[end] == '-') end++;
            while (end < json.Length && char.IsDigit(json[end]))
                end++;

            if (end > start)
            {
                string val = json.Substring(start, end - start);
                if (int.TryParse(val, out int result))
                    return result;
            }

            return 0;
        }

        private float ExtractFloat(string json, string key)
        {
            string search = $"\"{key}\"";
            int keyIdx = json.IndexOf(search);
            if (keyIdx < 0) return 0f;

            int colonIdx = json.IndexOf(':', keyIdx + search.Length);
            if (colonIdx < 0) return 0f;

            int start = colonIdx + 1;
            while (start < json.Length && (json[start] == ' ' || json[start] == '\t'))
                start++;

            int end = start;
            if (end < json.Length && json[end] == '-') end++;
            while (end < json.Length && (char.IsDigit(json[end]) || json[end] == '.'))
                end++;

            if (end > start)
            {
                string val = json.Substring(start, end - start);
                if (float.TryParse(val, System.Globalization.NumberStyles.Float,
                    System.Globalization.CultureInfo.InvariantCulture, out float result))
                    return result;
            }

            return 0f;
        }

        private string ExtractString(string json, string key)
        {
            string search = $"\"{key}\"";
            int keyIdx = json.IndexOf(search);
            if (keyIdx < 0) return "";

            int colonIdx = json.IndexOf(':', keyIdx + search.Length);
            if (colonIdx < 0) return "";

            int quoteStart = json.IndexOf('"', colonIdx + 1);
            if (quoteStart < 0) return "";

            int quoteEnd = json.IndexOf('"', quoteStart + 1);
            if (quoteEnd < 0) return "";

            return json.Substring(quoteStart + 1, quoteEnd - quoteStart - 1);
        }

        private int FindMatchingBrace(string s, int openIdx)
        {
            int depth = 0;
            for (int i = openIdx; i < s.Length; i++)
            {
                if (s[i] == '{') depth++;
                else if (s[i] == '}')
                {
                    depth--;
                    if (depth == 0) return i;
                }
            }
            return -1;
        }

        private void OnWSConnected()
        {
            Debug.Log("[AppManager] WebSocket connected");
        }

        private void OnWSDisconnected()
        {
            Debug.Log("[AppManager] WebSocket disconnected, retrying in 3s...");
            StartCoroutine(RetryWebSocket());
        }

        private IEnumerator RetryWebSocket()
        {
            yield return new WaitForSeconds(3f);
            if (wsClient != null && !wsClient.IsConnected)
            {
                wsClient.Connect();
            }
        }

        private void OnWSMessage(string message)
        {
            Debug.Log($"[AppManager] WS message received");

            try
            {
                string type = ExtractString(message, "type");

                switch (type)
                {
                    case "pipeline_state_updated":
                    case "occupancy_updated":
                    case "spatial_occupancy_updated":
                        HandleOccupancyUpdate(message);
                        break;
                    case "recommendation_changed":
                    case "redistribution_recommended":
                        HandleRecommendationUpdate(message);
                        break;
                    case "door_state_changed":
                        HandleDoorStateChange(message);
                        break;
                    case "bogie_health_updated":
                        HandleBogieHealthUpdate(message);
                        break;
                    case "announcement_generated":
                        Debug.Log("[AppManager] Announcement received");
                        break;
                    default:
                        PollState();
                        break;
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[AppManager] WS message parse error: {e.Message}");
            }
        }

        private void HandleDoorStateChange(string message)
        {
            int carId = ExtractInt(message, "car_id");
            string doorAction = ExtractString(message, "door_action");

            if (carId > 0 && !string.IsNullOrEmpty(doorAction))
            {
                Debug.Log($"[AppManager] Door state: Car {carId} = {doorAction}");
            }
        }

        private void HandleBogieHealthUpdate(string message)
        {
            int carId = ExtractInt(message, "car_id");
            float calesScore = ExtractFloat(message, "cales_score");
            float healthIndex = ExtractFloat(message, "health_index");
            int priority = ExtractInt(message, "inspection_priority");

            if (carId > 0)
            {
                Debug.Log($"[AppManager] Bogie health: Car {carId} CALES={calesScore:F2} Health={healthIndex:F1}% Priority={priority}");
            }
        }

        private void OnApiError(string error)
        {
            Debug.LogWarning($"[AppManager] API error: {error}");
        }

        public void LoadScenario(string scenarioName)
        {
            if (apiClient == null) return;

            apiClient.LoadScenario(scenarioName, (success) =>
            {
                if (success)
                {
                    Debug.Log($"[AppManager] Scenario loaded: {scenarioName}");
                    PollState();
                }
            });
        }

        public void ResetSimulation()
        {
            if (apiClient == null) return;

            apiClient.ResetSimulation((success) =>
            {
                if (success)
                {
                    Debug.Log("[AppManager] Simulation reset");
                    if (trainController != null) trainController.ResetTrain();
                }
            });
        }

        private void OnDestroy()
        {
            if (wsClient != null)
            {
                wsClient.OnConnected -= OnWSConnected;
                wsClient.OnDisconnected -= OnWSDisconnected;
                wsClient.OnMessageReceived -= OnWSMessage;
            }

            if (apiClient != null)
            {
                apiClient.OnError -= OnApiError;
            }
        }
    }
}
