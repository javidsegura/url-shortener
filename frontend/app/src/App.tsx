
import { Routes, Route } from "react-router-dom"

import AppLayout from "./layout/app_layout"

import Home from "./pages/Home"
import User from "./pages/User"
import URLLink from "./pages/URLLink"
import Auth from "./pages/Auth"
import PrivateRoutes from "./components/auth/routes/PrivateRoutes"

function App(){
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Home />} />
        <Route path="/auth" element={<Auth />} />
        <Route element={<PrivateRoutes />}>
          <Route path="/user/:id" element={<User />} />
          <Route path="/URLLink" element={<URLLink />} />
        </Route>
      </Route>
      <Route path="*" element={<p>404 error</p>} />
    </Routes>
  )
}


export default App
