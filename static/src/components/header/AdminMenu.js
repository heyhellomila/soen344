import React, {Component} from 'react'
import { Link } from 'react-router-dom'
import { logOut } from '../../actions/auth'


class AdminMenu extends Component {
    render() {
        return (
            <div>
                    Welcome {this.props.user.username}!
                    &nbsp;&nbsp;&nbsp;
                    <Link to="/register">
                        Register an Account
                    </Link>
                    &nbsp;&nbsp;&nbsp;
                    <Link to="/" onClick={logOut}>
                        Logout
                    </Link>
            </div> 
        );
    }
}


export default AdminMenu;