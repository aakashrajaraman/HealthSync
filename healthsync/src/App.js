import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/login.jsx";
import ClinicRegistration from "./pages/clinicRegistration.jsx";

function App() {
  return (
   
    <Router>
    <Routes>
      <Route path='/' element={<LoginPage />} />
      <Route path='/login' element={<LoginPage />} />
      <Route path='/clinicRegistration' element={<ClinicRegistration />} />

    </Routes>
  </Router>

  );
}

export default App;
