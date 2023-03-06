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
import {useState, useContext} from "preact/hooks";
import * as style from "./style.css";
import {FaCheckSquare, FaRegCheckSquare} from "react-icons/fa";

export interface Props {
    enabled: boolean
    callback: (state: boolean) => void;
}

const MaintenanceBlock: FunctionalComponent<Props> = (props) => {
    const [pressed, setPressed] = useState(props.enabled);

    /**
     * Toggle the checkbox, passing the new value to the callback method
     */
    const toggle = () => {
        props.callback(!pressed);
        setPressed(!pressed);
    }

    return (
        <div className={style.maintenanceBlock} onClick={() => toggle()}>
            <div style={{float: "left", width: "20%"}}>
                {pressed ? <FaCheckSquare size={48}/> : <FaRegCheckSquare size={48}/>}
            </div>
            <div style={{float: "right", width: "80%"}}>
                <label>Enable Maintenance Mode</label><br/>
                <small>Note: This will power on the SDI-12 sensors and increase power consumption.</small>
            </div>
        </div>
    )
}

export default MaintenanceBlock;
