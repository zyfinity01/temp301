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
import * as style from "./style.css"

type InfoProps = {
    icon: any;
    name: string;
    value: number|string;
    alert_level?: "info"|"warning"|"danger";
    extra?: string;
}

const InfoItem: React.FunctionComponent<InfoProps> = (props: InfoProps) => {

    const getColor = (color: "info"|"warning"|"danger"|undefined) => {
        switch (color) {
            case "warning": return {color:"#d69d00"};
            case "danger": return {color:"red"};
            case "info":
            default: return {color:"ccc"}
        }
    }

    return (
        <div class={style.item}>
            <span className={style.icon}>{props.icon}</span>
            <span className={style.name}>{props.name}</span>
            <span className={style.value} style={getColor(props.alert_level)}>{props.value}</span>
        </div>
    )
}

export default InfoItem;
