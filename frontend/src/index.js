import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import SimpleReactLightbox from "simple-react-lightbox";

import SignIn from "./components/pages/signin/SignIn";
import Layout from "./components/app";
import Transactions from "./components/pages/transactions/Transactions";

import "./index.css";
import "./index.scss";

class Root extends React.Component {
  render() {
    return (
      <BrowserRouter basename={"/"}>
        <SimpleReactLightbox>
          <Routes>
            <Route path="/signin" element={<SignIn />} />
            <Route path="/" element={<Layout />}>
              <Route path="transactions" element={<Transactions />} />
              {/* Additional routes can be nested here as needed */}
            </Route>
            {/* Default route to handle root, you can adjust if you want a specific component at the root */}
            <Route path="/" element={<SignIn />} />
          </Routes>
        </SimpleReactLightbox>
      </BrowserRouter>
    );
  }
}

ReactDOM.render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
  document.getElementById("root")
);
