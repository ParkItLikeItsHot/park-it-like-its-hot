import React, { useEffect, useState } from "react";

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

  return (
    <div>
      <h2>
        Amount of Cars in Parking Lot: {carCount === null ? "Loading..." : `${carCount} / ${maxCars}`}
      </h2>
      {error && <p style={{ color: "red" }}>Error: {error}</p>}

      <div
        className="progress"
        role="progressbar"
        aria-label="Basic example"
        aria-valuenow={carCount ?? 0}
        aria-valuemin={0}
        aria-valuemax={maxCars}
      >
        <div
          className="progress-bar"
          style={{ width: `${((carCount ?? 0) / maxCars) * 100}%` }}
        ></div>
      </div>
    </div>
  );
};

export default AmountOfCars;
