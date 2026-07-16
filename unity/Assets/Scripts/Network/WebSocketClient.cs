using System;
using System.Collections;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace Themis.Unity.Network
{
    public class WebSocketClient : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string wsUrl = "ws://localhost:8000/ws";
        [SerializeField] private float reconnectDelay = 3f;
        [SerializeField] private float heartbeatInterval = 30f;

        private ClientWebSocket _ws;
        private CancellationTokenSource _cts;
        private bool _isConnected = false;
        private float _lastHeartbeat;
        private Task _receiveTask;

        public event Action<string> OnMessageReceived;
        public event Action OnConnected;
        public event Action OnDisconnected;

        public bool IsConnected => _isConnected;

        private void Start()
        {
            Connect();
        }

        public void Connect()
        {
            if (_isConnected)
            {
                Debug.Log("[WS] Already connected");
                return;
            }

            Debug.Log($"[WS] Connecting to {wsUrl}...");
            _cts = new CancellationTokenSource();
            _ws = new ClientWebSocket();
            StartCoroutine(ConnectCoroutine());
        }

        public void Disconnect()
        {
            Debug.Log("[WS] Disconnecting...");
            _isConnected = false;

            if (_cts != null)
                _cts.Cancel();

            if (_ws != null)
            {
                try
                {
                    _ws.CloseAsync(
                        WebSocketCloseStatus.NormalClosure,
                        "Closing",
                        CancellationToken.None,
                        CancellationToken.None).Wait(1000);
                }
                catch { }
                _ws.Dispose();
                _ws = null;
            }

            OnDisconnected?.Invoke();
        }

        public void SendMessage(string message)
        {
            if (!_isConnected || _ws == null || _ws.State != WebSocketState.Open)
            {
                Debug.LogWarning("[WS] Cannot send - not connected");
                return;
            }

            StartCoroutine(SendMessageCoroutine(message));
        }

        private IEnumerator ConnectCoroutine()
        {
            Task connectTask = _ws.ConnectAsync(new Uri(wsUrl), _cts.Token);
            while (!connectTask.IsCompleted)
                yield return null;

            if (connectTask.IsFaulted || connectTask.IsCanceled)
            {
                string errorMsg = connectTask.Exception?.InnerException?.Message ?? "Unknown error";
                Debug.LogWarning($"[WS] Connection failed: {errorMsg}");
                yield return new WaitForSeconds(reconnectDelay);
                Connect();
                yield break;
            }

            _isConnected = true;
            _lastHeartbeat = Time.time;
            Debug.Log("[WS] Connected successfully");
            OnConnected?.Invoke();

            // Start receive loop in background thread
            _receiveTask = Task.Run(() => ReceiveLoop(_cts.Token));
        }

        private async Task ReceiveLoop(CancellationToken token)
        {
            var buffer = new byte[4096];

            while (_isConnected && _ws.State == WebSocketState.Open && !token.IsCancellationRequested)
            {
                try
                {
                    var result = await _ws.ReceiveAsync(new ArraySegment<byte>(buffer), token);

                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        Debug.Log("[WS] Server closed connection");
                        _isConnected = false;
                        UnityMainThreadDispatcher.Enqueue(() => OnDisconnected?.Invoke());
                        break;
                    }

                    if (result.MessageType == WebSocketMessageType.Text)
                    {
                        string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                        string msgCopy = message;
                        UnityMainThreadDispatcher.Enqueue(() => OnMessageReceived?.Invoke(msgCopy));
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception e)
                {
                    Debug.LogWarning($"[WS] Receive error: {e.Message}");
                    break;
                }
            }

            if (_isConnected)
            {
                _isConnected = false;
                UnityMainThreadDispatcher.Enqueue(() => OnDisconnected?.Invoke());
            }
        }

        private IEnumerator SendMessageCoroutine(string message)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(message);
            Task sendTask = _ws.SendAsync(
                new ArraySegment<byte>(bytes),
                WebSocketMessageType.Text,
                true,
                _cts.Token);

            while (!sendTask.IsCompleted)
                yield return null;

            if (sendTask.IsFaulted)
                Debug.LogWarning($"[WS] Send failed: {sendTask.Exception?.InnerException?.Message}");
        }

        private void OnDestroy()
        {
            Disconnect();
        }

        private void OnApplicationQuit()
        {
            Disconnect();
        }
    }

    /// <summary>
    /// Simple main thread dispatcher for invoking actions on Unity main thread.
    /// </summary>
    public static class UnityMainThreadDispatcher
    {
        private static readonly Queue<Action> _queue = new Queue<Action>();
        private static readonly object _lock = new object();

        public static void Enqueue(Action action)
        {
            lock (_lock)
            {
                _queue.Enqueue(action);
            }
        }

        /// <summary>
        /// Call this from a MonoBehaviour Update() method.
        /// </summary>
        public static void ProcessQueue()
        {
            lock (_lock)
            {
                while (_queue.Count > 0)
                {
                    Action action = _queue.Dequeue();
                    action?.Invoke();
                }
            }
        }
    }
}
