import React from "react";

export default function ModelTimeline({ models }) {
  return (
    <div>
      <h2 className="font-bold mb-2">Model Versions</h2>
      <ul>
        {models.map((m, i) => (
          <li key={i}>Round {m.round}: {m.cid}</li>
        ))}
      </ul>
    </div>
  );
}
