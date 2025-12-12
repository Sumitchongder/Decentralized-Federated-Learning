import React, { useEffect, useRef } from "react";
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from "chart.js";

Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale);

export default function RoundChart({ data }) {
  const chartRef = useRef(null);

  useEffect(() => {
    const ctx = chartRef.current.getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.map(d => d.round),
        datasets: [{ label: "Accuracy", data: data.map(d => d.accuracy), borderColor: "blue" }]
      }
    });
  }, [data]);

  return <canvas ref={chartRef}></canvas>;
}
