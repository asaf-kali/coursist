import React, {Component} from "react";
import {Header} from "./Header";

export class CoursistPage extends Component {
    constructor(props) {
        super(props);
        this.state = {...props}
    }

    renderHeader() {
        return "IMPLEMENT";
    }

    renderContent() {
        return "IMPLEMENT";
    }

    render() {
        return (
            <div>
                <Header inner_html={this.renderHeader()}/>
                <div id="content-body-container" style={{margin: 25 + "px"}}>
                    {this.renderContent()}
                </div>
            </div>
        );
    }
}