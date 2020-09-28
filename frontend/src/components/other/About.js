import React from "react";
import {CoursistPage} from "../main/CoursistPage";

export class About extends CoursistPage {
    constructor(props) {
        super(props);
    }

    renderHeader() {
        return (
            <div className="container-fluid text-center text-white">
                <br/><br/><br/>
                <div className="col-sm-12">
                    <h1>אודות הפרוייקט</h1>
                </div>
                <br/><br/>
            </div>
        );
    }

    renderContent() {
        return (
            <div className="card text-center card-form" style={{width: "720px", maxWidth: "90%"}}>
                <div className="card-header">
                    <h1>Coursist</h1>
                </div>
                <div className="card-body" style={{margin: "0 auto"}}>
                    <div className="card-text" style={{textAlign: "right"}}>
                        קורסיסט הוא פרוייקט קוד פתוח, ומהווה אב-טיפוס לאתר שיכול לשמש סטודנטים מכל רחבי העולם.<br/>
                        המטרות המרכזיות שהפרוייקט שואף לעמוד בהן:
                        <br/><br/>
                        <ol>
                            <li>
                                דירוג ובקרה חברתית של קורסים ומרצים על-ידי סטודנטים.
                            </li>
                            <li>
                                כלי עזר לתכנון מערכת שעות סמסטריאלית.
                            </li>
                            <li>
                                כלי עזר לתכנון מסלול התואר עד לסיומו.
                            </li>
                        </ol>
                    </div>
                    <br/>
                    <a href="https://github.com/asaf-kali/coursist" className="btn btn-primary">Go to github
                        repo</a>
                </div>
                <br/>
                <div className="card-text disclaimer">
                    * דיסקליימר: האתר נבנה בפרוייקט במסגרת הקורס "67118 - סדנא בקוד פתוח" של האוניברסיטה העברית,
                    ואין היוצרים שלו אחראיים על התכנים בו, אבטחתם ונכונותם.
                </div>
                <br/><br/>
                <div className="card-footer text-muted">
                    Created on April 2020
                </div>
            </div>
        );
    }
}