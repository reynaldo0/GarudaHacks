using System.Collections;
using UnityEngine;

namespace Themis.Unity.Train
{
    public class DoorController : MonoBehaviour
    {
        [Header("Door Settings")]
        [SerializeField] private Transform leftDoor;
        [SerializeField] private Transform rightDoor;
        [SerializeField] private float openOffset = 0.4f;
        [SerializeField] private float animationDuration = 1.5f;

        [Header("Door State")]
        [SerializeField] private string currentState = "CLOSE";
        [SerializeField] private bool isAnimating = false;

        private Vector3 _leftClosedPos;
        private Vector3 _rightClosedPos;
        private Vector3 _leftOpenPos;
        private Vector3 _rightOpenPos;
        private Coroutine _animationCoroutine;
        private bool _initialized = false;

        public string CurrentState => currentState;
        public bool IsAnimating => isAnimating;

        private void Start()
        {
            InitializeDoorPositions();
        }

        private void InitializeDoorPositions()
        {
            if (leftDoor != null)
            {
                _leftClosedPos = leftDoor.localPosition;
                _leftOpenPos = _leftClosedPos + Vector3.left * openOffset;
            }

            if (rightDoor != null)
            {
                _rightClosedPos = rightDoor.localPosition;
                _rightOpenPos = _rightClosedPos + Vector3.right * openOffset;
            }

            _initialized = (leftDoor != null || rightDoor != null);
        }

        public void SetDoorAction(string action)
        {
            if (action == currentState) return;

            currentState = action;

            if (!_initialized)
                InitializeDoorPositions();

            if (!_initialized) return;

            if (_animationCoroutine != null)
                StopCoroutine(_animationCoroutine);

            switch (action)
            {
                case "OPEN_MIDDLE":
                    _animationCoroutine = StartCoroutine(AnimateDoor(true));
                    break;
                case "CLOSE":
                default:
                    _animationCoroutine = StartCoroutine(AnimateDoor(false));
                    break;
            }
        }

        private IEnumerator AnimateDoor(bool opening)
        {
            isAnimating = true;

            float elapsed = 0f;
            Vector3 leftStart = leftDoor != null ? leftDoor.localPosition : Vector3.zero;
            Vector3 rightStart = rightDoor != null ? rightDoor.localPosition : Vector3.zero;
            Vector3 leftTarget = opening ? _leftOpenPos : _leftClosedPos;
            Vector3 rightTarget = opening ? _rightOpenPos : _rightClosedPos;

            while (elapsed < animationDuration)
            {
                elapsed += Time.deltaTime;
                float t = Mathf.SmoothStep(0f, 1f, elapsed / animationDuration);

                if (leftDoor != null)
                    leftDoor.localPosition = Vector3.Lerp(leftStart, leftTarget, t);

                if (rightDoor != null)
                    rightDoor.localPosition = Vector3.Lerp(rightStart, rightTarget, t);

                yield return null;
            }

            if (leftDoor != null)
                leftDoor.localPosition = leftTarget;
            if (rightDoor != null)
                rightDoor.localPosition = rightTarget;

            isAnimating = false;

            string stateStr = opening ? "OPEN" : "CLOSED";
            Debug.Log($"[Door] Car door {stateStr}");
        }

        public void CreateVisualDoors()
        {
            Transform carTransform = transform.parent != null ? transform.parent : transform;
            Bounds carBounds = GetCarBounds(carTransform);

            float doorWidth = 0.04f;
            float doorHeight = carBounds.size.y * 0.7f;
            float doorDepth = 0.3f;
            float doorY = carBounds.min.y + doorHeight * 0.5f + 0.05f;

            GameObject leftDoorObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            leftDoorObj.name = "Door_Left";
            leftDoorObj.transform.SetParent(transform);
            leftDoorObj.transform.localPosition = new Vector3(0f, doorY, carBounds.extents.z + 0.01f);
            leftDoorObj.transform.localScale = new Vector3(doorWidth, doorHeight, doorDepth);
            leftDoor = leftDoorObj.transform;
            Renderer lr = leftDoorObj.GetComponent<Renderer>();
            if (lr != null) lr.material.color = new Color(0.3f, 0.3f, 0.35f);

            GameObject rightDoorObj = GameObject.CreatePrimitive(PrimitiveType.Cube);
            rightDoorObj.name = "Door_Right";
            rightDoorObj.transform.SetParent(transform);
            rightDoorObj.transform.localPosition = new Vector3(0f, doorY, carBounds.extents.z + 0.01f);
            rightDoorObj.transform.localScale = new Vector3(doorWidth, doorHeight, doorDepth);
            rightDoor = rightDoorObj.transform;
            Renderer rr = rightDoorObj.GetComponent<Renderer>();
            if (rr != null) rr.material.color = new Color(0.3f, 0.3f, 0.35f);

            _initialized = true;
            InitializeDoorPositions();
        }

        private Bounds GetCarBounds(Transform t)
        {
            Renderer r = t.GetComponent<Renderer>();
            if (r != null) return r.bounds;

            Collider c = t.GetComponent<Collider>();
            if (c != null) return c.bounds;

            return new Bounds(t.position, new Vector3(2.5f, 2f, 1.5f));
        }
    }
}
