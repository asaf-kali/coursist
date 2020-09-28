import React, {Component} from "react";
import {render} from "react-dom";
import {BrowserRouter, Route} from "react-router-dom";
import {About} from "./other/About.js"
import {AllCourses} from "./courses/AllCourses";
import {MainNavBar} from "./main/Menu";

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {...props};
    }

    render() {
        return (
            <BrowserRouter>
                <MainNavBar is_anonymous={this.state.is_anonymous} is_staff={this.state.is_staff}/>
                <Route path='/alter/' component={AllCourses} exact/>
                <Route path='/alter/courses' component={AllCourses}/>
                <Route path='/alter/about' component={About}/>
            </BrowserRouter>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App/>, container);