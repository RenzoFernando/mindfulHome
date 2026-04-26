import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { Provider, useSelector } from "react-redux";

import store from "./features/store";
import App from "./App.jsx";
import "./index.css";

// Componente de debug
function DebugApp() {
const token = useSelector((state) => state.user.token);
const user = useSelector((state) => state.user.user);

useEffect(() => {
    console.log("DebugApp mounted");
    console.log("Token:", token);
    console.log("User:", user);
}, [token, user]);

return <App />;
}

// Render principal
const root = createRoot(document.getElementById("root"));

root.render( <Provider store={store}> <DebugApp /> </Provider>
);
