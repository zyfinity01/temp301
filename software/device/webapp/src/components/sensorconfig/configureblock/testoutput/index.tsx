// Copyright (C) 2023  Benjamin Secker, Jolon Behrent, Louis Li, James Quilty
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import React from "react";
import {FunctionalComponent, h} from "preact";
import Popup from "reactjs-popup";
import {SDIMessageType} from "../../../interfaces";
import * as componentstyle from "./style.css";

interface propType {
    name: string;
}

interface testType {
    response: {
        [reading: string]: number
    } | undefined;
}

const TestOutput: FunctionalComponent<propType> = (props) => {

    const [testResults, setTestResults] = React.useState<testType>({
        response: undefined
    });
    const [open, setOpen] = React.useState(false);

    const getData = (data: any) => {
        setOpen(true);
        console.log(data)
        console.log(`requesting test data from ${process.env.API_URL}config/sdi12/test/${props.name}`)
        fetch(`${process.env.API_URL}config/sdi12/test/${props.name}`)
            .then(res => res.json())
            .then(res => setTestResults(res))
            .catch(err => console.log(err));
    }

    const close = () => {
        setTestResults({response: undefined});
        setOpen(false);
    }

    return (
        <React.Fragment>
            <button
                onClick={getData}
                type="button"
                className={componentstyle.testButton}
            >
                Test Sensor
            </button>
            <Popup
                open={open}
                onClose={close}
                modal
                closeOnDocumentClick
                closeOnEscape
                className="popup"
            >
                <div>
                    <h3>Sensor data for {props.name}</h3>
                    <div className={componentstyle.results}>
                        {testResults.response
                            ? <pre>{JSON.stringify(testResults.response, null, 2)}</pre>
                            : "loading..."}
                    </div>
                    <button className={componentstyle.closeButton} onClick={close}>OK</button>
                </div>
            </Popup>
        </React.Fragment>
    )
}

export default TestOutput;
