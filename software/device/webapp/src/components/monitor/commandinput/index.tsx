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

import { h } from "preact";
import React from "react";
import * as style from './style.css'

interface propType {
    canSend: boolean; // lock
    callback: (message: string)=>void;
}

/**
 * Form for sending commands to device
 * @constructor
 */
const CommandInput: React.FunctionComponent<propType> = (props) => {

    const [message, setMessage] = React.useState("");

    const handleSubmit = (e: any) => {
        e.preventDefault();

        if (!props.canSend) {
            return;
        }

        props.callback(message);
        setMessage(''); // reset message
    }

    return (
        <form onSubmit={handleSubmit}>
            <input type="text" placeholder="Message..."
                   value={message}
                   onChange={(e: any) => setMessage(e.target.value)}
                   disabled={!props.canSend}
                   className={style.inputButton}
            />
            <input type="submit"
                   className={style.submitButton}
                   value="Send"
                   disabled={!props.canSend}/>
        </form>
    )
}

export default CommandInput;
