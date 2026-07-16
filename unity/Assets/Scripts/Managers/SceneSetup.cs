using UnityEngine;

namespace Themis.Unity.Managers
{
    public class SceneSetup : MonoBehaviour
    {
        [Header("Auto-Create")]
        [SerializeField] private bool autoCreateManagers = true;
        [SerializeField] private bool autoCreateTrain = true;

        private void Awake()
        {
            if (!autoCreateManagers) return;

            Debug.Log("[SceneSetup] Setting up scene...");

            GameObject networkObj = new GameObject("Network");
            networkObj.AddComponent<Network.ApiClient>();
            networkObj.AddComponent<Network.WebSocketClient>();

            if (autoCreateTrain)
            {
                GameObject trainObj = new GameObject("Train");
                trainObj.transform.position = new Vector3(-12f, 0, 0);
                trainObj.AddComponent<Train.TrainController>();
            }

            GameObject uiObj = new GameObject("UI");
            uiObj.AddComponent<UI.StatusBar>();

            if (AppManager.Instance == null)
            {
                GameObject managerObj = new GameObject("AppManager");
                managerObj.AddComponent<AppManager>();
            }

            Debug.Log("[SceneSetup] Scene setup complete!");
        }
    }
}
