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
import MessageBox from "./messagebox";
import CommandInput from "./commandinput";
import React from "react";
import { SDIMessageType } from "../interfaces";
import * as style from '../style.css'

const MonitorPage: React.FunctionComponent = () => {

    const [messageHistory, setMessageHistory] = React.useState<SDIMessageType[]>([]);
    const [canSend, setCanSend] = React.useState(true);

    const getCommandOutput = (message: string) => {
        setCanSend(false); // lock inputs while receiving data

        fetch(encodeURI(`${process.env.API_URL}monitor?command=${message}`),
            {
                credentials: 'same-origin',
                headers: {
                    "Content-Type": "application/json"
                }
            }
        )
            .then(res => res.json())
            .then((res: SDIMessageType) => {
                console.log(res);
                updateMessageList(res)
                setCanSend(true); // re-allow inputs
            })
            .catch(err => console.log(err));
    }

    const updateMessageList = (response: SDIMessageType) => {
        if (response.response != "") {
            setMessageHistory([...messageHistory, response]);
        }
    }


    return (
        // Apply custom formatting to the monitor div to ensure monitor output fills remaining space
        <div className={style.page} style={{display: 'flex', flexDirection: 'column'}}>
            <h2>Monitor</h2>
            <MessageBox messages={messageHistory}/>
            <CommandInput
                canSend={canSend}
                callback={(input) => {
                    getCommandOutput(input);
                }}/>
        </div>
    )
}

export default MonitorPage;
