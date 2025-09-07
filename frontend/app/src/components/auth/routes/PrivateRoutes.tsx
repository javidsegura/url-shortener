
import { useNavigate, Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../../hooks/useAuth";

export default function PrivateRoutes(){
      const [user, loading] = useAuth()

      if (loading){
            return <div> Flying spinner baby!!! </div>
      }
      if (!user){
            return <Navigate to="/auth" />
      }
      return <Outlet />

}