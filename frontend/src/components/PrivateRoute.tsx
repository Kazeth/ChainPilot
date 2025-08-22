import { useAuthContext } from "@/context/AuthContext"
import { Navigate, Outlet } from "react-router-dom";

export default function PrivateLayout(){
    const auth = useAuthContext();
    if(auth.isAuthenticated){
        return <Outlet />;
    } else {
        return <Navigate to="/" />;
    }
}