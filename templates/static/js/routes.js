import React from 'react';
import { HashRouter, Route, hashHistory } from 'react-router-dom';
import Home from './components/Home';
import Predictions from './components/Predictions';
import Actual from './components/Actual';

// import more components
export default (
    <HashRouter history={hashHistory}>
     <div>
      <Route path='/' component={Home} />
      <Route path='/predictions' component={Predictions} /> 
      <Route path='/actual' component={Actual} /> 
     </div>
    </HashRouter>
);