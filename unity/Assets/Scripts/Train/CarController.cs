using UnityEngine;
using Themis.Unity.Indicators;
using Themis.Unity.Visualization;

namespace Themis.Unity.Train
{
    public class CarController : MonoBehaviour
    {
        [Header("Car Settings")]
        [SerializeField] private int carId = 1;

        [Header("Visualization")]
        [SerializeField] private Renderer bodyRenderer;
        [SerializeField] private Material greenMaterial;
        [SerializeField] private Material yellowMaterial;
        [SerializeField] private Material redMaterial;

        [Header("Density Indicator")]
        [SerializeField] private LEDIndicator ledIndicator;

        [Header("Door")]
        [SerializeField] private DoorController doorController;

        [Header("Bogie Dashboard")]
        [SerializeField] private BogieDashboard bogieDashboard;

        [Header("Occupancy Display")]
        [SerializeField] private UI.OccupancyDisplay occupancyDisplay;

        [Header("4x Ceiling Fisheye Cameras")]
        [SerializeField] private Camera.CameraSimulator[] ceilingCameras = new Camera.CameraSimulator[4];
        [SerializeField] private Network.ApiClient apiClient;
        [SerializeField] private bool autoCreateCameras = true;

        [Header("Camera Layout (ceiling-mounted, pointing down)")]
        [SerializeField] private float ceilingHeight = 2.2f;
        [SerializeField] private float camFrontOffset = 0.5f;
        [SerializeField] private float camRearOffset = -0.5f;
        [SerializeField] private float camLeftOffset = -0.4f;
        [SerializeField] private float camRightOffset = 0.4f;

        private float _occupancyRatio = 0f;
        private string _densityIndicator = "GREEN";
        private float _freeSpaceRatio = 1f;
        private float _spatialOccupancyScore = 0f;
        private string _doorAction = "CLOSE";
        private string _recommendedTarget = null;
        private string _announcement = null;
        private float _calesScore = 0f;
        private float _healthIndex = 100f;
        private float _damageMultiplier = 1f;
        private int _inspectionPriority = 0;
        private string _recommendedAction = "CONTINUE_MONITORING";

        private bool _camerasCreated = false;
        private Material _cachedMaterial;

        public int CarId => carId;
        public float OccupancyRatio => _occupancyRatio;
        public string DensityIndicator => _densityIndicator;
        public float FreeSpaceRatio => _freeSpaceRatio;
        public string DoorAction => _doorAction;
        public string RecommendedTarget => _recommendedTarget;

        public void Initialize(int id)
        {
            carId = id;
            gameObject.name = $"Car_{id}";
            if (bodyRenderer == null)
                bodyRenderer = GetComponent<Renderer>();
            UpdateSpatialOccupancy(0f, "GREEN");
        }

        public void SetCarId(int id)
        {
            carId = id;
            gameObject.name = $"Car_{id}";
        }

        public void CreateCeilingFisheyeCameras(Network.ApiClient sharedApiClient)
        {
            if (_camerasCreated) return;

            apiClient = sharedApiClient;

            Vector3[] localPositions = new Vector3[]
            {
                new Vector3(camLeftOffset, ceilingHeight, camFrontOffset),
                new Vector3(camRightOffset, ceilingHeight, camFrontOffset),
                new Vector3(camLeftOffset, ceilingHeight, camRearOffset),
                new Vector3(camRightOffset, ceilingHeight, camRearOffset),
            };

            for (int i = 0; i < 4; i++)
            {
                GameObject camObj = new GameObject($"ceiling_cam_{carId:D2}_{i + 1:D2}");
                camObj.transform.SetParent(transform);
                camObj.transform.localPosition = localPositions[i];
                camObj.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);

                UnityEngine.Camera cam = camObj.AddComponent<UnityEngine.Camera>();
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = new Color(0.1f, 0.1f, 0.15f);
                cam.fieldOfView = 170f;
                cam.nearClipPlane = 0.05f;
                cam.farClipPlane = 10f;
                cam.depth = -1;

                Camera.CameraSimulator sim = camObj.AddComponent<Camera.CameraSimulator>();
                sim.SetCameraId($"car{carId:D2}_cam{i + 1:D2}");
                sim.SetTrainId("SF10-001");
                sim.SetFisheye(true, 170f);

                if (apiClient != null)
                    sim.SetApiClient(apiClient);

                ceilingCameras[i] = sim;
            }

            _camerasCreated = true;
            Debug.Log($"[Car {carId}] 4 ceiling fisheye cameras created: car{carId:D2}_cam01..cam04");
        }

        public void StartCameraCapture()
        {
            if (!_camerasCreated) return;

            for (int i = 0; i < ceilingCameras.Length; i++)
            {
                if (ceilingCameras[i] != null)
                    ceilingCameras[i].StartCapture();
            }

            Debug.Log($"[Car {carId}] All 4 ceiling cameras capturing");
        }

        public void StopCameraCapture()
        {
            for (int i = 0; i < ceilingCameras.Length; i++)
            {
                if (ceilingCameras[i] != null)
                    ceilingCameras[i].StopCapture();
            }
        }

        public void UpdateSpatialOccupancy(float occupancyRatio, string densityIndicator)
        {
            _occupancyRatio = Mathf.Clamp01(occupancyRatio);
            _densityIndicator = densityIndicator;
            _freeSpaceRatio = 1f - _occupancyRatio;
            _spatialOccupancyScore = _occupancyRatio;
            UpdateVisual();
            UpdateLED();
            UpdateOccupancyDisplay();
        }

        public void ApplyPipelineState(
            float occupancyRatio,
            string densityIndicator,
            float freeSpaceRatio,
            string doorAction,
            string recommendedTarget,
            string announcement,
            float calesScore,
            float healthIndex,
            float damageMultiplier,
            int inspectionPriority,
            string recommendedAction)
        {
            _occupancyRatio = Mathf.Clamp01(occupancyRatio);
            _densityIndicator = densityIndicator;
            _freeSpaceRatio = freeSpaceRatio;
            _spatialOccupancyScore = _occupancyRatio;
            _doorAction = doorAction;
            _recommendedTarget = recommendedTarget;
            _announcement = announcement;
            _calesScore = calesScore;
            _healthIndex = healthIndex;
            _damageMultiplier = damageMultiplier;
            _inspectionPriority = inspectionPriority;
            _recommendedAction = recommendedAction;

            UpdateVisual();
            UpdateLED();
            UpdateDoor();
            UpdateOccupancyDisplay();
            UpdateBogieDashboard();
        }

        private void UpdateVisual()
        {
            if (bodyRenderer == null) return;

            Material targetMaterial = greenMaterial;
            Color targetColor = new Color(0.15f, 0.68f, 0.38f);

            switch (_densityIndicator)
            {
                case "GREEN":
                    targetColor = new Color(0.15f, 0.68f, 0.38f);
                    if (greenMaterial != null) targetMaterial = greenMaterial;
                    break;
                case "YELLOW":
                    targetColor = new Color(1f, 0.75f, 0.0f);
                    if (yellowMaterial != null) targetMaterial = yellowMaterial;
                    break;
                case "RED":
                    targetColor = new Color(0.95f, 0.25f, 0.05f);
                    if (redMaterial != null) targetMaterial = redMaterial;
                    break;
                default:
                    targetColor = Color.gray;
                    break;
            }

            if (_cachedMaterial != null)
            {
                bodyRenderer.material = _cachedMaterial;
            }
            else if (targetMaterial != null)
            {
                _cachedMaterial = targetMaterial;
                bodyRenderer.material = targetMaterial;
            }
            else
            {
                bodyRenderer.material.color = targetColor;
            }
        }

        private void UpdateLED()
        {
            if (ledIndicator == null)
                ledIndicator = GetComponentInChildren<LEDIndicator>();

            if (ledIndicator != null)
            {
                ledIndicator.SetState(_densityIndicator);
            }
        }

        private void UpdateDoor()
        {
            if (doorController == null)
                doorController = GetComponentInChildren<DoorController>();

            if (doorController != null)
            {
                doorController.SetDoorAction(_doorAction);
            }
        }

        private void UpdateOccupancyDisplay()
        {
            if (occupancyDisplay == null)
                occupancyDisplay = GetComponentInChildren<UI.OccupancyDisplay>();

            if (occupancyDisplay != null)
            {
                occupancyDisplay.UpdateDisplay(_occupancyRatio * 100f, _densityIndicator);
            }
        }

        private void UpdateBogieDashboard()
        {
            if (bogieDashboard == null)
                bogieDashboard = GetComponentInChildren<BogieDashboard>();

            if (bogieDashboard != null)
            {
                bogieDashboard.UpdateDashboard(_calesScore, _healthIndex, _damageMultiplier, _inspectionPriority, _recommendedAction);
            }
        }

        private void OnDestroy()
        {
            StopCameraCapture();
        }
    }
}
