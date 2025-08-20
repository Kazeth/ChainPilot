/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from '@ic-reactor/react';
import { Actor, HttpAgent } from '@dfinity/agent';
// import { Principal } from '@dfinity/principal';

const identityProvider = 'https://identity.ic0.app';

type AuthContextType = {
  isAuthenticated: boolean;
//   principal: Principal;
  login: () => void;
  logout: () => void;
  loginLoading: boolean;
  loginError: string;
  actor: Actor | null;
  authChecked?: boolean;
};

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
//   principal: Principal.anonymous(),
  login: async () => {},
  logout: async () => {},
  loginError: '',
  loginLoading: false,
  actor: null,
  authChecked: false,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const { authenticated, login, logout, loginLoading, identity, loginError } =
    useAuth();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
//   const [principal, setPrincipal] = useState<Principal>();
  const [actor, setActor] = useState<Actor | null>(null);
  const [authChecked, setAuthChecked] = useState(false);

  const handleLogin = () => {
    console.log()
    login({
      identityProvider,
    });
  };
  const handleLogout = async () => {
    logout();
    setIsAuthenticated(false);
    // setPrincipal(Principal.anonymous());
    setActor(null);
    console.log('logout success');
  };

  const checkAuth = async () => {
    try {
      console.log(identity?.getPrincipal().toText(), 'identity principal');
      if (authenticated) {
        // if (!identity) {
        //   console.error('Identity is null, cannot create HttpAgent.');
        //   return;
        // }
        // const agent = new HttpAgent({ identity });

        // if (process.env.NODE_ENV !== 'production') {
        //   await agent.fetchRootKey();
        // }
        // setIsAuthenticated(true);
        // setPrincipal(identity.getPrincipal());
      } else {
        console.log('AuthClient not logged in');
      }
    } catch (error) {
      console.error('Authentication check failed:', error);
    } finally {
      setAuthChecked(true);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  useEffect(() => {
    setIsAuthenticated(authenticated);
    if (authenticated) {
      checkAuth();
    }
  }, [authenticated]);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        // principal: identity ? identity.getPrincipal() : Principal.anonymous(),
        login: handleLogin,
        logout: handleLogout,
        loginLoading,
        loginError: loginError ?? '',
        actor,
        authChecked,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the AuthContext
export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};