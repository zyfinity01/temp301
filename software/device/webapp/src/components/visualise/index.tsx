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
import { useState } from "preact/hooks";
import InfoItem from "./infoitem";
import { FaSignal, FaBatteryFull, FaCheck, FaClock, FaSdCard, FaExclamation, FaDownload } from "react-icons/fa"
import { deviceDataType } from "../interfaces";
import * as style from "../style.css"
import { formatDateTime, timestampToDate } from "../../util";

const visualise: React.FunctionComponent<deviceDataType> = (props) => {

    // TODO google "ternary three options js"
    const signalAlertLevel = props.coverage_level > 50 ? "info" : props.coverage_level > 15 ? "warning" : "danger";
    const batteryAlertLevel = props.battery_level > 50 ? "info" : props.battery_level > 15 ? "warning" : "danger";

    // convert timestamps to human-readable form
    const [transmittedDate, transmittedTime] = formatDateTime(timestampToDate(props.last_transmitted));
    const last_sent = `${transmittedDate} ${transmittedTime}`;

    const [updatedDate, updatedTime] = formatDateTime(timestampToDate(props.last_transmitted));
    const last_updated = `${updatedDate} ${updatedTime}`;

    const [modemOn, toggleModem] = useState(false);
    const handleButtonClick = () => {
        toggleModem(!modemOn);
    }

    return (
        <div className={style.page}>
            <h2>Visualise</h2>

            <button className = {[style.bigButton, modemOn ? style.bigButtonRed : ""].join(" ")}
                   onClick={handleButtonClick} >
                {modemOn ? "Turn Modem Off" : "Turn Modem On"}
            </button>

            <InfoItem icon={<FaSignal/>} name="Signal" value={`${props.coverage_level}%`}
                      alert_level={signalAlertLevel}/>
            <InfoItem icon={<FaBatteryFull/>} name="Battery Level" value={`${props.battery_level}%`}
                      alert_level={batteryAlertLevel}/>
            <InfoItem icon={<FaCheck/>} name="Messages Sent" value={props.messages_sent}/>
            <InfoItem icon={<FaExclamation/>} name="Messages Failed" value={props.failed_transmissions}/>
            <InfoItem icon={<FaClock/>} name={`Last Message Sent`} value={last_sent}/>
            <InfoItem icon={<FaDownload/>} name={`Last Updated`} value={last_updated}/>
            <InfoItem icon={<FaSdCard/>} name={`SD Card Free Space`} value={`${props.free_sd_space} MB`}/>

            <button className={style.bigButton}
                   style={{
                       padding: '10px',
                       fontSize: '18px'
                   }}
            >
                Download Device Data
            </button>
        </div>
    )
};

export default visualise;
