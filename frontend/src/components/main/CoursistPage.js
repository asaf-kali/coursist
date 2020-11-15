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

    updateState(data) {
        const newState = {...this.state, ...data}
        this.setState(newState)
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