import React, { Component } from 'react';
import { Outlet } from 'react-router-dom';

class Layout extends Component {
    render() {
        return (
            <>
                <Outlet />  {/* Nested routes will be rendered here */}
            </>
        );
    }
}

export default Layout;
