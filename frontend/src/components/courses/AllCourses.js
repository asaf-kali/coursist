import React, {Component} from "react";
import {CoursistPage} from "../main/CoursistPage";
import {CourseBlock} from "./CourseBlock";
import "./Courses.css"
import {Redirect} from 'react-router-dom'

export const RedirectToAllCourses = () => {
    return <Redirect to='/courses'/>
}

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
        fetch("/api/courses/")
            .then(response => {
                if (response.status > 400) {
                    this.setState({placeholder: "Something went wrong!"});
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data)
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