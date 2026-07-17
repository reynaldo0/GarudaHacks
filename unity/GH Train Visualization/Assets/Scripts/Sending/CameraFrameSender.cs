using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

/// <summary>
/// Capture 4 kamera fisheye (via Render Texture) dan kirim sebagai
/// multipart/form-data ke POST /api/v1/frame setiap N detik.
/// </summary>
public class CameraFrameSender : MonoBehaviour
{
    [Header("Konfigurasi Server")]
    [SerializeField] private string baseUrl = "https://api.themis.my.id";
    [SerializeField] private string apiKey = "da1GdehRzd59b71fwyeJDkuXY151hOO_uhIYpDSbNwazer4y3sWudjMNREYLq4Y_";

    [Header("Kereta & Stasiun")]
    [SerializeField] private string trainId = "SF10-001";
    [SerializeField] private string stationId = "manggarai";

    [Header("4 Kamera Fisheye (drag di Inspector)")]
    [SerializeField] private Camera[] cameras = new Camera[4];
    [SerializeField] private string[] cameraIds = { "cam01", "cam02", "cam03", "cam04" };

    [Header("Interval Kirim (detik)")]
    [SerializeField] private float sendInterval = 5f;

    private void Start()
    {
        // Validasi dasar biar error jelas kalau ada yang lupa di-drag
        if (cameras.Length != 4)
        {
            Debug.LogError("[CameraFrameSender] Harus ada tepat 4 kamera di array 'cameras'.");
            return;
        }

        foreach (var cam in cameras)
        {
            if (cam.targetTexture == null)
            {
                Debug.LogError($"[CameraFrameSender] Kamera '{cam.name}' belum punya Target Texture (Render Texture). " +
                                "Set dulu di Inspector sebelum jalan.");
                return;
            }
        }

        StartCoroutine(SendFrameLoop());
    }

    private IEnumerator SendFrameLoop()
    {
        while (true)
        {
            yield return StartCoroutine(CaptureAndSendFrame());
            yield return new WaitForSeconds(sendInterval);
        }
    }

    private IEnumerator CaptureAndSendFrame()
    {
        // 1. Capture tiap kamera ke byte[] JPG
        byte[][] jpgBytesList = new byte[cameras.Length][];

        for (int i = 0; i < cameras.Length; i++)
        {
            jpgBytesList[i] = CaptureCameraToJPG(cameras[i]);
        }

        // for (int i = 0; i < cameras.Length; i++)
        // {
        //     Debug.Log($"{cameraIds[i]} -> {jpgBytesList[i].Length} bytes");
        // }

        // 2. Susun multipart form
        List<IMultipartFormSection> formData = new List<IMultipartFormSection>();

        for (int i = 0; i < jpgBytesList.Length; i++)
        {
            formData.Add(new MultipartFormFileSection(
                "files",                       // nama field harus "files" sesuai API
                jpgBytesList[i],
                $"{cameraIds[i]}.jpg",
                "image/jpeg"
            ));
        }

        formData.Add(new MultipartFormDataSection("cameraIds", string.Join(",", cameraIds)));
        formData.Add(new MultipartFormDataSection("stationId", stationId));
        formData.Add(new MultipartFormDataSection("trainId", trainId));

        // 3. Kirim POST request
        string url = $"{baseUrl}/api/v1/frame";
        using (UnityWebRequest request = UnityWebRequest.Post(url, formData))
        {
            request.SetRequestHeader("X-API-Key", apiKey);

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log($"[CameraFrameSender] Frame terkirim. Response: {request.downloadHandler.text}");
            }
            else
            {
                Debug.LogError($"[CameraFrameSender] Gagal kirim frame: {request.error}\n" +
                                $"Response: {request.downloadHandler.text}");
            }
        }
    }

    /// <summary>
    /// Ambil hasil render dari sebuah Camera (via Render Texture yang sudah
    /// di-assign ke targetTexture-nya) lalu encode jadi JPG bytes.
    /// </summary>
    private byte[] CaptureCameraToJPG(Camera cam)
    {
        RenderTexture rt = cam.targetTexture;

        // Simpan RenderTexture aktif sebelumnya, lalu set punya kita
        RenderTexture previousActive = RenderTexture.active;
        RenderTexture.active = rt;

        // Paksa kamera render sekali (biar frame terbaru)
        cam.Render();

        // Baca pixel dari RenderTexture ke Texture2D
        Texture2D tex = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
        tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
        tex.Apply();

        RenderTexture.active = previousActive;

        byte[] jpgBytes = tex.EncodeToJPG(85); // 85 = kualitas kompresi

        Destroy(tex); // cleanup, hindari memory leak

        return jpgBytes;
    }
}
