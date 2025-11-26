import React, { useEffect, useState } from "react";
import "./AmountOfCars.css";

const AmountOfCars: React.FC = () => {
  const [carCount, setCarCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchCount = async () => {
      try {
        const res = await fetch("http://localhost:6767/cars-in-parking-lot");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const count = Number(
          data?.cars_in_parking_lot ?? data?.carsInParkingLot ?? 0
        );
        if (mounted) {
          setCarCount(Number.isFinite(count) ? count : 0);
          setError(null);
        }
      } catch (err: any) {
        if (mounted) setError(err?.message ?? "Failed to fetch");
      }
    };

    // initial fetch
    fetchCount();
    // poll every 3 seconds
    const id = setInterval(fetchCount, 3000);

    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  const maxCars = 5; // Set your max cars value here
  const percentage = Math.min(100, Math.max(0, ((carCount ?? 0) / maxCars) * 100));

  return (
    <div className="parking-card">
      <h2 className="parking-title">Parking Status</h2>
      
      {carCount === null ? (
        <div className="loading-text">Connecting to sensors...</div>
      ) : (
        <div className="parking-status">
          <div className="count-display">{carCount}</div>
          <div className="max-capacity">out of {maxCars} spots occupied</div>
        </div>
      )}

      {error && <div className="error-message">Connection Error: {error}</div>}

      <div className="progress-container">
        <div
          className="progress-fill"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={carCount ?? 0}
          aria-valuemin={0}
          aria-valuemax={maxCars}
        ></div>
      </div>
    </div>
  );
};

export default AmountOfCars;
