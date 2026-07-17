using UnityEngine;

public class CarSeverity : MonoBehaviour
{
    public StateReceiver stateReceiver;

    void Update()
    {
        switch (stateReceiver.currentSeverity)
        {
            case "LOW":
                Debug.Log("LOW");
                break;

            case "MEDIUM":
                Debug.Log("MEDIUM");
                break;

            case "HIGH":
                Debug.Log("HIGH");
                break;

            case "CRITICAL":
                Debug.Log("CRITICAL");
                break;

            default:
                Debug.Log("NOTHING");
                break;
        }
    }
}
