import React, {Component} from "react";
import {NavLink,} from "react-router-dom";

export class MainNavBar extends Component {
    constructor(props) {
        super(props);
        this.state = {
            is_staff: props.is_staff,
            is_anonymous: props.is_anonymous
        }
    }

    render() {
        return (
            <nav className="navbar fixed-top navbar-expand-lg navbar-light bg-navbar">
                <NavLink className="navbar-brand" to="/alter/">Coursist</NavLink>
                <button className="navbar-toggler" type="button" data-toggle="collapse"
                        data-target=".dual-collapse" aria-expanded="false"
                        aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"/>
                </button>
                <div className="collapse navbar-collapse dual-collapse w-100 order-1">
                    <ul className="navbar-nav mr-auto">
                        <li className="nav-item">
                            <NavLink className="nav-link" to="/alter/courses">קורסים</NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink className="nav-link" to="/alter/schedule">בניית מערכת</NavLink>
                        </li>
                        <li className="nav-item">
                            <NavLink className="nav-link" to="/alter/about/">אודות</NavLink>
                        </li>
                        {this.state.is_staff &&
                        <>
                            <li className="nav-item">
                                <NavLink className="nav-link" to="/alter/degree-program">תכנון מסלול</NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink className="nav-link" to="/alter/admin:index">ניהול</NavLink>
                            </li>
                        </>
                        }
                    </ul>
                </div>
                <div className="collapse navbar-collapse dual-collapse w-100 order-2">
                    <ul className="navbar-nav ml-auto">
                        {this.state.is_anonymous ?
                            (<>
                                <li className="nav-item">
                                    <NavLink className="nav-link" to="/alter/account_login">התחברות</NavLink>
                                </li>
                                <li className="nav-item">
                                    <NavLink className="nav-link" to="/alter/account_signup">הרשמה</NavLink>
                                </li>
                            </>) : (<>
                                {/*<li className="nav-item">*/}
                                {/*    <NavLink className="nav-link"*/}
                                {/*             to="{% url 'user' user.username %}">שלום {{user}}</NavLink>*/}
                                {/*</li>*/}
                                {/*<li className="nav-item">*/}
                                {/*    <form method="post" action="{% url 'account_logout' %}" style="margin: 0 auto;">*/}
                                {/*        /!*{% csrf_token %}*!/*/}
                                {/*        {% if redirect_field_value %}*/}
                                {/*        <input type="hidden" name="{{ redirect_field_name }}"*/}
                                {/*               value="{{ redirect_field_value }}"/>*/}
                                {/*        {% endif %}*/}
                                {/*        <button type="submit" className="sign-out-btn nav-link">התנתקות</button>*/}
                                {/*    </form>*/}
                                {/*</li>*/}
                            </>)
                        }
                    </ul>
                </div>
            </nav>
        )
    }
}