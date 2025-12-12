import React from "react";

export default function NodeList({ nodes }) {
  return (
    <div>
      <h2 className="font-bold mb-2">Nodes Status</h2>
      <ul>
        {Object.entries(nodes).map(([id, n]) => (
          <li key={id}>{id}: {n.status}</li>
        ))}
      </ul>
    </div>
  );
}
