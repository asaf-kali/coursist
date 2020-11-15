import React, {Component} from "react";
import {render} from "react-dom";
import {BrowserRouter, Route} from "react-router-dom";
import {About} from "./other/About.js"
import {AllCourses, RedirectToAllCourses} from "./courses/AllCourses";
import {CourseDetails} from "./courses/CourseDetails";
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
                <Route path='/' component={RedirectToAllCourses} exact/>
                <Route path='/courses/' component={AllCourses} exact />
                <Route path='/courses/:id/' component={CourseDetails} exact/>
                <Route path='/about/' component={About}/>
            </BrowserRouter>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App/>, container);