using System;
using System.Collections.Generic;
using UnityEngine;

namespace Themis.Unity.Train
{
    public class TrainController : MonoBehaviour
    {
        [Header("Train Settings")]
        [SerializeField] private string trainId = "SF10-001";
        [SerializeField] private int totalCars = 10;
        [SerializeField] private GameObject carPrefab;
        [SerializeField] private float carSpacing = 3.0f;

        [Header("Highlight")]
        [SerializeField] private Color sourceHighlightColor = new Color(1f, 0.3f, 0.1f);
        [SerializeField] private Color targetHighlightColor = new Color(0.1f, 0.9f, 0.3f);

        private List<CarController> _cars = new List<CarController>();
        private int _highlightedSource = -1;
        private int _highlightedTarget = -1;

        public string TrainId => trainId;
        public List<CarController> Cars => _cars;

        private void Start()
        {
            InitializeTrain();
        }

        public void InitializeTrain()
        {
            Debug.Log($"[Train] Initializing {totalCars} cars...");

            for (int i = 0; i < totalCars; i++)
            {
                Vector3 position = transform.position + new Vector3(i * carSpacing, 0, 0);
                GameObject carObj;

                if (carPrefab != null)
                {
                    carObj = Instantiate(carPrefab, position, Quaternion.identity, transform);
                }
                else
                {
                    carObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    carObj.transform.position = position;
                    carObj.transform.SetParent(transform);
                    carObj.transform.localScale = new Vector3(2.5f, 1.8f, 1.4f);

                    BoxCollider col = carObj.GetComponent<BoxCollider>();
                    if (col == null) col = carObj.AddComponent<BoxCollider>();
                }

                carObj.name = $"Car_{i + 1}";
                carObj.tag = "TrainCar";

                CarController car = carObj.GetComponent<CarController>();
                if (car == null)
                {
                    car = carObj.AddComponent<CarController>();
                }
                car.Initialize(i + 1);
                _cars.Add(car);
            }

            Debug.Log($"[Train] Train initialized with {_cars.Count} cars");
        }

        public void SetTrainId(string id)
        {
            trainId = id;
        }

        public void UpdateCarSpatialOccupancy(int carId, float occupancyRatio, string densityIndicator)
        {
            if (carId < 1 || carId > _cars.Count)
            {
                Debug.LogWarning($"[Train] Invalid car ID: {carId}");
                return;
            }

            _cars[carId - 1].UpdateSpatialOccupancy(occupancyRatio, densityIndicator);
        }

        public void ApplyPipelineStateToCar(PipelineStateData state)
        {
            if (state.carId < 1 || state.carId > _cars.Count)
            {
                Debug.LogWarning($"[Train] Invalid car ID: {state.carId}");
                return;
            }

            _cars[state.carId - 1].ApplyPipelineState(
                state.occupancyRatio,
                state.densityIndicator,
                state.freeSpaceRatio,
                state.doorAction,
                state.recommendedTarget,
                state.announcement,
                state.calesScore,
                state.healthIndex,
                state.damageMultiplier,
                state.inspectionPriority,
                state.recommendedAction
            );
        }

        public void UpdateAllCars(PipelineStateData[] states)
        {
            if (states == null) return;

            foreach (var state in states)
            {
                ApplyPipelineStateToCar(state);
            }
        }

        public void HighlightRecommendedCar(int fromCar, int toCar)
        {
            ClearHighlights();

            _highlightedSource = fromCar;
            _highlightedTarget = toCar;

            if (fromCar >= 1 && fromCar <= _cars.Count)
            {
                SetCarHighlightColor(fromCar, sourceHighlightColor);
            }

            if (toCar >= 1 && toCar <= _cars.Count)
            {
                SetCarHighlightColor(toCar, targetHighlightColor);
            }

            Debug.Log($"[Train] Recommendation: Car {fromCar} -> Car {toCar}");
        }

        public void ClearHighlights()
        {
            if (_highlightedSource >= 1 && _highlightedSource <= _cars.Count)
            {
                CarController src = _cars[_highlightedSource - 1];
                src.UpdateSpatialOccupancy(src.OccupancyRatio, src.DensityIndicator);
            }

            if (_highlightedTarget >= 1 && _highlightedTarget <= _cars.Count)
            {
                CarController tgt = _cars[_highlightedTarget - 1];
                tgt.UpdateSpatialOccupancy(tgt.OccupancyRatio, tgt.DensityIndicator);
            }

            _highlightedSource = -1;
            _highlightedTarget = -1;
        }

        private void SetCarHighlightColor(int carIndex, Color color)
        {
            if (carIndex < 1 || carIndex > _cars.Count) return;

            CarController car = _cars[carIndex - 1];
            Renderer r = car.GetComponent<Renderer>();
            if (r != null)
            {
                r.material.color = color;
            }
        }

        public void ResetTrain()
        {
            ClearHighlights();
            foreach (var car in _cars)
            {
                car.UpdateSpatialOccupancy(0f, "GREEN");
            }
        }

        [Serializable]
        public class PipelineStateData
        {
            public int carId;
            public float occupancyRatio;
            public float freeSpaceRatio;
            public string densityIndicator;
            public float spatialOccupancyScore;
            public string recommendedTarget;
            public string doorAction;
            public string announcement;
            public float calesScore;
            public float healthIndex;
            public float damageMultiplier;
            public int inspectionPriority;
            public string recommendedAction;
        }
    }
}
