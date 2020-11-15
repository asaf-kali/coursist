import React, {Component} from "react";
import {NavLink,} from "react-router-dom";

export class CourseBlock extends Component {
    constructor(props) {
        super(props);
        this.state = {
            id: props.id,
            course_number: props.course_number,
            name: props.name,
            score: props.score,
        }
    }

    getLink() {
        return `/courses/${this.state.id}/`;
    }

    render() {
        return (
            <div className="card float-left course-block course-block-link">
                <NavLink to={this.getLink()} className="course-block-link">
                <span className="course-block-score">
                    {this.state.score} כוכבים
                </span>
                    <div className="card-body text-center">
                        <h6 className="card-subtitle mb-2 text-muted font-weight-bold">
                            <br/>{this.state.course_number}
                        </h6>
                        <h5 className="card-title black">{this.state.name}</h5>
                    </div>
                </NavLink>
            </div>
        )
    }
}