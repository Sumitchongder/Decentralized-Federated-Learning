import React from "react";

export default function TransactionFeed({ txs }) {
  return (
    <div>
      <h2 className="font-bold mb-2">Blockchain Transactions</h2>
      <ul>
        {txs.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>
    </div>
  );
}
