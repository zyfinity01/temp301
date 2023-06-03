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

import { FunctionalComponent, h } from "preact";
import * as style from "./style.css";
import DarkModeToggle from "./dark_mode_toggle";

type PropTypes = {
    deviceName: string;
    deviceID: string;
}

const Header: FunctionalComponent<PropTypes> = ({deviceName, deviceID}) => {
    return (
        <div class={style.header}>
            <DarkModeToggle />
            <h1>{deviceName}</h1>
            <h3>{deviceID}</h3>
        </div>
    );
};

export default Header;
