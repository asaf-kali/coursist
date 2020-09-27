import React, {Component} from "react";
import {render} from "react-dom";

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            loaded: false,
            placeholder: "Loading"
        };
    }

    componentDidMount() {
        fetch("api/course/")
            .then(response => {
                if (response.status > 400) {
                    return this.setState(() => {
                        return {placeholder: "Something went wrong!"};
                    });
                }
                return response.json();
            })
            .then(data => {
                this.setState(() => {
                    return {
                        data,
                        loaded: true
                    };
                });
            });
    }

    render() {
        return (
            <ul>
                {this.state.data.map(course => {
                    return (
                        <li key={course.id}>
                            {course.course_number} | {course.name}
                        </li>
                    );
                })}
            </ul>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App/>, container);