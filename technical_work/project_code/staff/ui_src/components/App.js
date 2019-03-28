import React from "react";
import ReactDOM from "react-dom";
import DataProvider from "./DataProvider";
import SessionTable from "./SessionTable";
const App = () => (
  <DataProvider endpoint="api/lecture/123/sessions"
                render={data => <Table data={data} />} />
);
const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App />, wrapper) : null;
