import React, { useEffect, useState } from "react";
import axios from "axios";
import ModelTimeline from "../components/ModelTimeline";

export default function Models() {
  const [models, setModels] = useState([]);

  useEffect(() => {
    async function fetchModels() {
      const res = await axios.get("http://localhost:8000/models");
      setModels(res.data);
    }
    fetchModels();
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Models</h1>
      <ModelTimeline models={models} />
    </div>
  );
}
