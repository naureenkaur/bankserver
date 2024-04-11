import React from "react";
import { Navigate, useLocation } from "react-router-dom";

const SignInProtectedRoute = ({ children }) => {
  const authenticated = sessionStorage.getItem("authenticated");

  if (authenticated) {
    // Redirect them to the /signin page, but save the current location they were
    // trying to go to when they were redirected. This allows us to send them
    // along to that page after they login, which is a nicer user experience
    // than dropping them off on the home page.
    return <Navigate to="/Transactions" />;
  }

  return children;
};

export default SignInProtectedRoute;
