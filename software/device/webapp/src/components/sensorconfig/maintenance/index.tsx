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
import Popup from "reactjs-popup";
import {useState, useContext} from "preact/hooks";
import * as style from "./style.css";
import {FaCheckSquare, FaRegCheckSquare} from "react-icons/fa";

export interface Props {
    enabled: boolean
    callback: (state: boolean) => void;
}

const MaintenanceBlock: FunctionalComponent<Props> = (props) => {
    const [pressed, setPressed] = useState(props.enabled);
    // For popup window functionality
    const [showPopup, setShowPopup] = useState(false);

    /**
     * Toggle the checkbox, passing the new value to the callback method
     */
    const toggle = () => {
        props.callback(!pressed);
        setPressed(!pressed);
    }
    /**
     *  Inital functionality as seen in the first block;
     *  Includes a notice functionality letting the user know that the sensor has been succesfully enabled
     *
     *  The popup window functionality is set within the second block where implementation has been copied over from the
     *  Rename sensor popup window within: software\device\webapp\src\components\sensorconfig\configureblock\rename\index.tsx
     *  Redirected the initial toggle function to only be set after clicking the "Yes" button within the popup window.
     *
     */
    return (
        <div>
            <div className={style.maintenanceBlock} onClick={() => setShowPopup(true)}>
                <div style={{float: "left", width: "20%"}}>
                    {pressed ? <FaCheckSquare size={48} color="green"/> : <FaRegCheckSquare size={48}/>}
                </div>
                <div style={{float: "right", width: "80%"}}>
                    <label>{pressed ? 'You are in maintanence mode!' : 'Maintanence mode is currently not enabled'} </label><br/>
                    <small>Click here if you wish to <b>{!pressed ? 'enter' : 'exit'}</b> maitenance mode</small>
                </div>
            </div>
            <Popup open={showPopup} onClose={() => setShowPopup(false)} modal>
                <div>
                    <h3>Maintenance Mode Note</h3>
                    <p>Do you wish to continue?</p>
                    <p>This will power <b>{!pressed ? 'on' : 'off'}</b> the SDI-12 sensors and increase power consumption.</p>
                    <input type={"submit"}
                        value={!pressed ? 'Enable Maintenance Mode' : 'Exit Maintenance Mode'}
                        onClick={() => {
                            toggle();
                            setShowPopup(false);
                        }}
                        className={style.bigButton}
                    />
                    <input type={"submit"}
                        value={"Cancel"}
                        onClick={() => {
                            setShowPopup(false);
                        }}
                        className={style.bigButton}
                    />
                </div>
            </Popup>
        </div>
                /* <div style={{float: "left", width: "20%"}}>
                    {pressed ? <FaCheckSquare size={48}/> : <FaRegCheckSquare size={48}/>}
                </div>
                <div style={{float: "right", width: "80%"}}>
                    <label>Enable Maintenance Mode</label><br/>
                    <small>Note: This will power on the SDI-12 sensors and increase power consumption.</small>
                </div>
            </div> */
    )
}
export default MaintenanceBlock;
