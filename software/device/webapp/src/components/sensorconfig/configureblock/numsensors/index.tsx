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

import { h, FunctionalComponent } from "preact";
import Popup from "reactjs-popup";
import { FaHashtag } from "react-icons/fa";
import { useState } from "preact/hooks";
import * as style from '../../../style.css';

interface PropTypes {
    readings: number;
    callback: (num: number) => void;
}

const NumSensorsModal: FunctionalComponent<PropTypes> = (props) => {

    const [number, setNumber] = useState(props.readings)

    const handleSubmit = (e: any, close: ()=> void) => {
        e.preventDefault();
        console.log("Number of sensors: " + number);
        if (0 < number && number <= 10) {
            props.callback(number);
            close();
        }
    }

    return (
        <Popup
            trigger={<button><FaHashtag/>Readings</button>}
            closeOnDocumentClick
            modal
        >
            {close => (
                <div>
                    <h3>Number of Readings</h3>
                    <form onSubmit={(e) => handleSubmit(e, close)}>
                        <input type={"number"}
                               value={number}
                               onChange={(e: any) => setNumber(e.target.value)}
                               required
                               min={1}
                               max={10}
                               style={{
                                   width: "100%",
                                   marginBottom: "5px"
                               }}
                        />
                        <input type={"submit"}
                               value={"OK"}
                               className={style.bigButton}
                        />
                    </form>
                </div>
            )}
        </Popup>
    )
}

export default NumSensorsModal;
