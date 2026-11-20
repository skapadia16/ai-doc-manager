// =====================================================
// src/context/AuthContext.jsx — Login state management
// =====================================================
// React Context: Poore app mein user info share karta hai
// Login/Logout yahan handle hota hai

import { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // App start hone par check karo — user pehle se logged in hai?
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      authAPI.me()
        .then((res) => setUser(res.data))
        .catch(() => localStorage.clear())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // Login function — token save karo, user set karo
  const login = async (email, password) => {
    const res = await authAPI.login({ email, password });
    const { access_token, ...userData } = res.data;
    localStorage.setItem("token", access_token);
    setUser(userData);
    return userData;
  };

  // Logout — sab clear karo
  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook — easy use ke liye
export const useAuth = () => useContext(AuthContext);
