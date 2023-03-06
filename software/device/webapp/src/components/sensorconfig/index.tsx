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

import {Component, FunctionalComponent, h} from "preact";
import * as style from "../style.css";
import {deviceConfigType, SDISensorType} from "../interfaces";
import SDISensorConfigBlock, {Props} from "./configureblock";
import {useForm} from "react-hook-form";
import MaintenanceBlock from "./maintenance";
import AddSensorModal from "./addsensor";
import {useContext} from "preact/hooks";
import {request} from "../../util/apiClient";
import {getNotyfContext} from "../../util/notyfContext";

const SensorConfigPage: FunctionalComponent<deviceConfigType> = (props) => {

    const {register, handleSubmit, watch, errors} = useForm<SDISensorType>();
    const notyf = getNotyfContext();

    /**
     * Set the maintenance mode of the device
     */
    const setMaintenance = (state: boolean) => {
        request({
            url: `${process.env.API_URL}config`,
            method: 'POST',
            init_message: (state ? 'Enabling' : 'Disabling') + " maintenance mode...",
            success_message: 'Maintenance mode set!',
            body: JSON.stringify({"maintenance_mode": state})
        }, notyf);
    }

    return (
        <div className={style.page}>
            <h2>Configure</h2>
            <MaintenanceBlock enabled={props.maintenance_mode} callback={(state) => setMaintenance(state)}/>

            <h3>Sensor Settings</h3>
            {props.sdi12_sensors !== undefined ? Object.keys(props.sdi12_sensors).map(sensor =>
                <SDISensorConfigBlock
                    name={sensor}
                    sensor={props.sdi12_sensors[sensor]}
                />) : <p>loading sensors...</p>
            }
            <br/>
            <AddSensorModal/>
        </div>
    )
}

export default SensorConfigPage;
