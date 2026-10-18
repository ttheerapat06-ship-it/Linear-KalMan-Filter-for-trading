
import numpy as np

from config import FIXED_Q, FIXED_R


class NumPyKalmanFilter:
    """2D State-Space Kalman Filter (Price & Velocity Estimation)"""

    def __init__(
        self,
        q_var: float = FIXED_Q,
        r_var: float = FIXED_R,
        initial_price: float = 50000.0,
    ):
        self.x = np.array([[initial_price], [0.0]])  # State: [Price, Velocity]
        self.P = np.array([[10.0, 0.0], [0.0, 10.0]])  # State Covariance
        self.A = np.array([[1.0, 1.0], [0.0, 1.0]])  # Transition Matrix
        self.H = np.array([[1.0, 0.0]])  # Measurement Matrix
        self.Q = np.eye(2) * q_var  # Process Noise Covariance
        self.R = np.array([[r_var]])  # Measurement Noise Covariance

    def update(self, z_price: float):
        x_pred = self.A @ self.x
        P_pred = self.A @ self.P @ self.A.T + self.Q

        y = np.array([[z_price]]) - (self.H @ x_pred)
        S = self.H @ P_pred @ self.H.T + self.R
        K = P_pred @ self.H.T @ np.linalg.inv(S)

        self.x = x_pred + (K @ y)
        self.P = (np.eye(2) - (K @ self.H)) @ P_pred

        return float(self.x[0, 0]), float(self.x[1, 0])
