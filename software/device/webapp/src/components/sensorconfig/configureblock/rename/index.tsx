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

import {h, FunctionalComponent} from "preact";
import Popup from "reactjs-popup";
import {FaEdit} from "react-icons/fa";
import {useState} from "preact/hooks";
import * as style from '../../../style.css';

interface PropTypes {
    name: string;
    callback: (name: string) => void;
}

const RenameModal: FunctionalComponent<PropTypes> = (props) => {

    const [name, setName] = useState(props.name);

    const handleSubmit = (e: any) => {
        e.preventDefault();
        props.callback(name);
    }

    return (
        <Popup
            trigger={<button><FaEdit/>Rename</button>}
            closeOnDocumentClick
            modal
        >
            {(close : any) => (
                <div>
                    <h3>Rename Sensor</h3>
                    <form>
                        <input type={"input"}
                               value={name}
                               onChange={(e: any) => setName(e.target.value)}
                               required
                               style={{
                                   width: "100%",
                                   marginBottom: "5px"
                               }}
                        />
                        <input type={"submit"}
                               value={"OK"}
                               onClick={(e) => {
                                   handleSubmit(e);
                                   close();
                               }}
                               className={style.bigButton}
                        />
                    </form>
                </div>
            )}
        </Popup>
    )
}

export default RenameModal;
