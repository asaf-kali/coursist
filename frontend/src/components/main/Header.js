import React, {Component} from "react";

export class Header extends Component {

    constructor(props) {
        super(props);
        this.state = {
            inner_html: props.inner_html
        };
    }

    render() {
        return (
            <div>
                <section className="container-fluid px-0">
                    <div className="row mr-0">
                        <div className="col-md-12 px-0">
                            <div className="header-image card">
                                <div className="opaque-wrapper" style={{minHeight: "inherit"}}>
                                    {this.state.inner_html}
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        )
    }

}