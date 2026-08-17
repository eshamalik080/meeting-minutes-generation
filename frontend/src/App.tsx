import { Route, Routes } from "react-router-dom";

import ErrorBoundary from "./components/ErrorBoundary";
import Navbar from "./components/Navbar";
import Landing from "./pages/Landing";
import NotFound from "./pages/NotFound";
import Workspace from "./pages/Workspace";

function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/app" element={<Workspace />} />
          <Route path="/app/:jobId" element={<Workspace />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </ErrorBoundary>
    </div>
  );
}

export default App;
