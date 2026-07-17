using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;

public class StateReceiver : MonoBehaviour
{
    [Header("Server Configuration")]
    [SerializeField] private string baseUrl = "https://api.themis.my.id";
    [SerializeField] private string apiKey = "da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_";

    [Header("Polling")]
    [SerializeField] private float pollInterval = 5f;

    [Header("Current Warning Severity")]
    public string currentSeverity = "NONE";

    private void Start()
    {
        StartCoroutine(PollStateLoop());
    }

    private IEnumerator PollStateLoop()
    {
        while (true)
        {
            yield return StartCoroutine(GetState());
            yield return new WaitForSeconds(pollInterval);
        }
    }

    private IEnumerator GetState()
    {
        string url = $"{baseUrl}/api/v1/state";

        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            request.SetRequestHeader("X-API-Key", apiKey);

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                StateResponse response =
                    JsonUtility.FromJson<StateResponse>(request.downloadHandler.text);

                if (response != null &&
                    response.data != null &&
                    response.data.warning != null)
                {
                    currentSeverity = response.data.warning.severity;
                }
                else
                {
                    currentSeverity = "NONE";
                }

                Debug.Log("Current Severity: " + currentSeverity);
            }
            else
            {
                Debug.LogError("Failed to get state: " + request.error);
            }
        }
    }

    [Serializable]
    public class StateResponse
    {
        public bool success;
        public StateData data;
    }

    [Serializable]
    public class StateData
    {
        public WarningData warning;
    }

    [Serializable]
    public class WarningData
    {
        public string severity;
    }
}