import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SimpleReactLightbox from 'simple-react-lightbox';

import DefaultLayout from './components/pages/signin/SignIn';
import Layout from './components/app';

import Transactions from './components/pages/transactions/Transactions';

import './index.css';
import './index.scss';

class Root extends React.Component {
    render() {
        return (
            <BrowserRouter basename={'/'}>
                <SimpleReactLightbox>
                    <Routes>
                        <Route path="/signin" element={<DefaultLayout />} />
                        <Route path="/" element={<DefaultLayout />} />

                        {/* Nested routes inside Layout component */}
                        <Route path="/" element={<Layout />}>
                            <Route path="transactions" element={<Transactions />} />
                            {/* Send all pages that do not exist to error page */}
                        </Route>
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
    document.getElementById('root')
);
