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

type TabProps = {
    // active button
    active: number;
    // callback function for button press
    click: (button: number) => void;
    // Toggle monitor button
    fullscreen: boolean;
}
const Tabs: React.FunctionComponent<TabProps> = ({ click, active, fullscreen }) => {

    const activeOutline = (button: number) => {
        return active == button ? {borderBottom: "#0d99a5 2px solid"} : undefined
    }

    return (
        <div className={style.tabbar}>
            <p className={style.tabs}>
                <a className={style.button} onClick={() => click(0)} style={activeOutline(0)}>VISUALISE</a>
                <a className={style.button} onClick={() => click(1)} style={activeOutline(1)}>DEVICE</a>
                <a className={style.button} onClick={() => click(2)} style={activeOutline(2)}>SENSORS</a>
                <a className={style.button} onClick={() => click(3)} style={activeOutline(3)}>HISTORY</a>
                { fullscreen ? null : <a className={style.button} onClick={() => click(4)} style={activeOutline(4)}>MONITOR</a> }
            </p>
        </div>
    )
}

export default Tabs;
