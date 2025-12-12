import React, { useEffect, useState } from "react";
import axios from "axios";
import RoundChart from "../components/RoundChart";
import NodeList from "../components/NodeList";

export default function Dashboard() {
  const [metrics, setMetrics] = useState([]);
  const [nodes, setNodes] = useState({});

  useEffect(() => {
    async function fetchData() {
      const metricsRes = await axios.get("http://localhost:8000/metrics");
      setMetrics(metricsRes.data);
      const nodesRes = await axios.get("http://localhost:8000/nodes");
      setNodes(nodesRes.data);
    }
    fetchData();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <RoundChart data={metrics} />
      <NodeList nodes={nodes} />
    </div>
  );
}
