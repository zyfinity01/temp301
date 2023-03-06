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

import {h, FunctionalComponent} from 'preact';
import React from "react";
import Popup from 'reactjs-popup';
import * as style from '../../style.css';
import * as componentStyle from './style.css';
import {useContext} from "preact/hooks";
import { getNotyfContext } from "../../../util/notyfContext";
import {fetchApiContext, request} from "../../../util/apiClient";

const AddSensorModal: FunctionalComponent = (props) => {

    const [name, setName] = React.useState('');
    const getConfig = useContext(fetchApiContext);
    const notyf = getNotyfContext();

    const handleSubmit = (e: any) => {
        e.preventDefault();

        request({
            url: `${process.env.API_URL}config/sdi12/update/${name}`,
            method: "POST",
            init_message: "Creating sensor...",
            success_message: "Sensor created successfully!",
            success_callback: () => getConfig(),
        }, notyf);
    }

    return (
        <Popup trigger={<button className={style.bigButton}>Add SDI-12 Sensor</button>}
               position="top center"
               closeOnDocumentClick>
            <div>
                <h3>Create New Sensor</h3>
                <small>(Letters, numbers and underscores only)</small>
                <form onSubmit={handleSubmit}>
                    <input className={componentStyle.name}
                           type="text"
                           placeholder="sensor name (unique)"
                           onChange={(e: any) => setName(e.target.value)}
                           required
                    />
                    <input type="submit" value="Create" className={style.bigButton}/>
                </form>
            </div>
        </Popup>
    )
}

export default AddSensorModal;
