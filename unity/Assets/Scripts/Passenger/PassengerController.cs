using UnityEngine;

namespace Themis.Unity.Passenger
{
    public class PassengerController : MonoBehaviour
    {
        private int _passengerId;
        private int _currentCar;
        private bool _isMoving;
        private Vector3 _targetPosition;

        public int PassengerId => _passengerId;
        public int CurrentCar => _currentCar;
        public bool IsMoving => _isMoving;

        [SerializeField] private float moveSpeed = 2f;

        public void Initialize(int id, int carId)
        {
            _passengerId = id;
            _currentCar = carId;
        }

        public void MoveToCar(int targetCarId)
        {
            _currentCar = targetCarId;
        }

        public void MoveToPosition(Vector3 worldPosition)
        {
            _targetPosition = worldPosition;
            _isMoving = true;
        }

        private void Update()
        {
            if (!_isMoving) return;

            transform.position = Vector3.MoveTowards(
                transform.position, _targetPosition, moveSpeed * Time.deltaTime);

            if (Vector3.Distance(transform.position, _targetPosition) < 0.01f)
            {
                transform.position = _targetPosition;
                _isMoving = false;
            }
        }
    }
}
