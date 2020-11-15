import React from "react";
import {CoursistPage} from "../main/CoursistPage";
import "./Courses.css"

export class CourseDetails extends CoursistPage {

    constructor(props) {
        super(props);
        this.state = {id: props.match.params.id, course: null, placeholder: "Loading"};
    }

    componentDidMount() {
        fetch(`/api/courses/${this.state.id}/`)
            .then(response => {
                if (response.status > 400) {
                    this.setState({placeholder: "Something went wrong!"});
                    return null;
                }
                return response.json()
            })
            .then(data => {
                this.updateState({course: data});
            })
        ;
    }

    get course() {
        return this.state.course;
    }

    renderLoading() {
        return (
            <div>
                This is page for course {this.state.id}, {this.state.placeholder}.
            </div>
        );
    }

    renderPage() {
        return (
            <div>
                {JSON.stringify(this.course)}
            </div>
        );
    }

    renderContent() {
        return this.course ? this.renderPage() : this.renderLoading();
    }
}