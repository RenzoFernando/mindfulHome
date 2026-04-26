import { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { setUser } from "../features/userSlice";

export const useUserData = () => {
    const dispatch = useDispatch();
    const token = useSelector(state => state.user.token);
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchUserData = async () => {
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const response = await fetch("http://localhost:8000/mindfulhome/users/me", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            
            if (!response.ok) throw new Error("Error fetching user data");
            
            const data = await response.json();
            dispatch(setUser(data));
            setUserData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUserData();
    }, [token]);

    return { userData, loading, error, refetch: fetchUserData };
};