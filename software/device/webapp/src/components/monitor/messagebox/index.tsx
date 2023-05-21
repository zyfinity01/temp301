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

import {FunctionalComponent, h} from "preact";
import {SDIMessageType} from "../../interfaces";

interface propTypes {
    messages: SDIMessageType[];
}

/**
 * Displays data received by the sensor.
 * @constructor
 */
const MessageBox: React.FunctionComponent<propTypes> = (props) => {
    return (
        <div style={wrapperStyle}>
            <div style={headerStyle}>
                Raw Command Output
            </div>
            <div style={MessagesSentStyle}>
                {props.messages.map(message =>
                    !("error" in message) ?
                        <span><i>{message.command + ": "}</i>{message.response}<br/></span>
                        :
                        <span><b>Error: </b>{message.error}<br/></span>
                )}
            </div>
        </div>
    )
}

const wrapperStyle = {
    "minHeight": "20px",
    // "padding": "5px",
    "marginBottom": "10px",
    "height": "100%",
    "borderRadius": "4px",
    "color": "var(--fg-colour)"
}

const headerStyle = {
    "backgroundColor": "#5c5c5c",
    "padding": "10px",
    "fontSize": "18px"
}

const MessagesSentStyle = {
    "minHeight": "20px",
    "backgroundColor": "var(--mid-colour)",
    "fontFamily": "\"Courier New\", Courier, monospace",
    "color": "var(--fg-colour)",
    "overflow": "scroll",
    "height": "calc(100% - 40px)",
    "padding": "5px",
};
export default MessageBox;
