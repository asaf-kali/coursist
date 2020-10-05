import React, {Component} from "react";
import {CoursistPage} from "../main/CoursistPage";
import {CourseBlock} from "./CourseBlock";
import "./Courses.css"

export class AllCourses extends CoursistPage {

    constructor(props) {
        super(props);
        this.state = {
            data: [],
            loaded: false,
            placeholder: "Loading"
        };
    }

    componentDidMount() {
        fetch("/api/course/")
            .then(response => {
                if (response.status > 400) {
                    return this.setState(() => {
                        return {placeholder: "Something went wrong!"};
                    });
                }
                return response.json();
            })
            .then(data => {
                this.setState({data: data, loaded: true});
            });
    }

    renderContent() {
        return this.state.loaded ? (
            <div className="container course-list">
                {
                    this.state.data.map(course => {
                        return <CourseBlock key={"course-block-" + course.id} {...course} />
                    })
                }
            </div>
        ) : (
            <div>
                סטטוס: {this.state.placeholder}
            </div>

        )

    }
}