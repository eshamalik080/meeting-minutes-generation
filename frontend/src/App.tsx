import { Route, Routes } from "react-router-dom";

import Navbar from "./components/Navbar";
import Landing from "./pages/Landing";
import Workspace from "./pages/Workspace";

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/app" element={<Workspace />} />
        <Route path="/app/:jobId" element={<Workspace />} />
      </Routes>
    </div>
  );
}

export default App;
