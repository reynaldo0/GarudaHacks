using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

/// <summary>
/// Polling GET /api/v1/occupancy secara berkala, lalu tampilkan
/// carId dan densityIndicator (severity) tiap gerbong di Console.
/// </summary>
public class OccupancyPoller : MonoBehaviour
{
    [Header("Konfigurasi Server")]
    [SerializeField] private string baseUrl = "http://localhost:8000";
    [SerializeField] private string apiKey = "themis-unity-key-2026";

    [Header("Filter (opsional)")]
    [SerializeField] private string trainId = "SF10-001"; // kosongkan ("") kalau tidak mau filter

    [Header("Interval Polling (detik)")]
    [SerializeField] private float pollInterval = 5f;

    private void Start()
    {
        StartCoroutine(PollLoop());
    }

    private IEnumerator PollLoop()
    {
        while (true)
        {
            yield return StartCoroutine(FetchOccupancy());
            yield return new WaitForSeconds(pollInterval);
        }
    }

    private IEnumerator FetchOccupancy()
    {
        string url = $"{baseUrl}/api/v1/occupancy";
        if (!string.IsNullOrEmpty(trainId))
        {
            url += $"?train_id={UnityWebRequest.EscapeURL(trainId)}";
        }

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("X-API-Key", apiKey);

            yield return request.SendWebRequest();

            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError($"[OccupancyPoller] Gagal ambil data: {request.error}\n" +
                                $"Response: {request.downloadHandler.text}");
                yield break;
            }

            string json = request.downloadHandler.text;
            OccupancyResponse response = JsonUtility.FromJson<OccupancyResponse>(json);

            if (response == null || !response.success || response.data == null)
            {
                Debug.LogWarning($"[OccupancyPoller] Response tidak valid atau kosong: {json}");
                yield break;
            }

            LogOccupancyPerCar(response.data);
        }
    }

    private void LogOccupancyPerCar(OccupancyData data)
    {
        if (data.cars == null || data.cars.Length == 0)
        {
            Debug.LogWarning("[OccupancyPoller] Tidak ada data 'cars' di response.");
            return;
        }

        System.Text.StringBuilder sb = new System.Text.StringBuilder();
        sb.AppendLine($"[OccupancyPoller] Train {data.trainId} @ {data.station} ({data.timestamp})");

        foreach (CarOccupancy car in data.cars)
        {
            sb.AppendLine($"  Car {car.carId}: {car.densityIndicator} " +
                           $"(occupancy={car.occupancyRatio:P0}, camera={car.cameraStatus})");
        }

        Debug.Log(sb.ToString());
    }
}

// ---------- Data classes untuk parsing JSON (harus [Serializable] biar JsonUtility bisa baca) ----------

[System.Serializable]
public class OccupancyResponse
{
    public bool success;
    public OccupancyData data;
}

[System.Serializable]
public class OccupancyData
{
    public string trainId;
    public string station;
    public string timestamp;
    public CarOccupancy[] cars;
}

[System.Serializable]
public class CarOccupancy
{
    public int carId;
    public float occupancyRatio;
    public float freeSpaceRatio;
    public string densityIndicator;
    public float spatialOccupancyScore;
    public string cameraStatus;
    public string cameraId;
    public float riskScore;
    public CarPrediction prediction;
}

[System.Serializable]
public class CarPrediction
{
    public string trend;
    public float predictedOccupancyRatio;
    public float confidence;
    public int horizonMinutes;
}
