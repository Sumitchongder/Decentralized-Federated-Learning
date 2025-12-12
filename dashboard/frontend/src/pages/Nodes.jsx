import React, { useEffect, useState } from "react";
import axios from "axios";
import NodeList from "../components/NodeList";

export default function Nodes() {
  const [nodes, setNodes] = useState({});

  useEffect(() => {
    async function fetchNodes() {
      const res = await axios.get("http://localhost:8000/nodes");
      setNodes(res.data);
    }
    fetchNodes();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Nodes</h1>
      <NodeList nodes={nodes} />
    </div>
  );
}
