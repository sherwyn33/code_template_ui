import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ObjectDetails from "./components/ObjectDetails";
import {DataContextProvider} from "./DataContextProvider";

const App = () => {
  return (
    <div className="app-container">
      {/* If you're using a context */}
      <DataContextProvider>
        {/* If you're using routing */}
        <Router>
          <Routes>
            {/* Define various routes */}
            <Route path="/" Component={ObjectDetails} />
            {/*<Route Component={<div>Not Found!</div>} />*/}

            {/* Add other routes as needed */}
          </Routes>
        </Router>
      </DataContextProvider>
    </div>
  );
}

export default App;
