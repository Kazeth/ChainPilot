import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainLayout from "./layout/MainLayout";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import LoadingPage from "./pages/Loading";
import AnalyticsPage from "./pages/AnalyticsAI";
import Portofolio from "./pages/Portofolio";
import Wallet from "./pages/Wallet";
import { useAuthContext } from "./context/AuthContext";
import NotFound from "./pages/NotFound";

function App() {
  const auth = useAuthContext();

  if (auth.loginLoading) {
    return <LoadingPage />;
  }

  return (
    <Router>
      {/* <MainLayout> */}
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/portfolio" element={<Portofolio />} />
          <Route path="/wallet" element={<Wallet />} />
        </Route>
        <Route path="/*" element={<NotFound />} />
      </Routes>
      {/* </MainLayout> */}
    </Router>
  );
}

export default App;
