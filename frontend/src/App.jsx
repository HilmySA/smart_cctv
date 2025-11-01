import './App.css'

import { BrowserRouter, Routes, Route, useParams } from "react-router-dom";
import Webcam from "./pages/pageWebcam";

function App() {

  return (
    <>
      <BrowserRouter>
      <Routes>
        <Route path="/webcam" element={<Webcam />} />
      </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
