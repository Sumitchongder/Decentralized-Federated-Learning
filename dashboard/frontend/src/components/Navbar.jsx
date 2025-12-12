import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-blue-600 p-4 text-white flex gap-4">
      <Link to="/">Dashboard</Link>
      <Link to="/models">Models</Link>
      <Link to="/nodes">Nodes</Link>
    </nav>
  );
}
