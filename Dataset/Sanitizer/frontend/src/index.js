import App from "./CropApp";
import React from 'react'
import ReactDOM from 'react-dom'
import CookiesProvider from "react-cookie/cjs/CookiesProvider";

const rootElement = document.getElementById('root')
ReactDOM.render(<CookiesProvider><App/></CookiesProvider>, rootElement)
