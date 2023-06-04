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

import React from "react";
import { useForm } from "react-hook-form";
import { FunctionalComponent, h } from "preact";
import { SDISensorType } from "../../interfaces";
import * as style from "../../style.css";
import * as componentstyle from "./style.css";
import { FaArrowDown, FaArrowUp, FaTrash } from "react-icons/fa"
import TestOutput from "./testoutput";
import { useContext } from "preact/hooks";
import { fetchApiContext, request } from "../../../util/apiClient";
import { getNotyfContext } from "../../../util/notyfContext";
import NumSensorsModal from "./numsensors";
import RenameModal from "./rename";

export interface Props {
    name: string;
    sensor: SDISensorType
}

const ConfigureBlock: FunctionalComponent<Props> = (props) => {
    const {register, handleSubmit} = useForm<SDISensorType>({
        defaultValues: {
            enabled: props.sensor.enabled,
            address: props.sensor.address,
            bootup_time: props.sensor.bootup_time,
            record_interval: props.sensor.record_interval,
            readings: props.sensor.readings
        }
    });

    const [opened, setOpened] = React.useState(false);
    const [numReadings, setNumReadings] = React.useState(props.sensor.readings.length);
    const ref = React.useRef(null);
    const notyf = getNotyfContext();
    const getConfig = useContext(fetchApiContext);

    let readings = [...props.sensor.readings];
    // Truncate the readings to the maximum length of the form
    if (numReadings < readings.length) {
        readings = readings.slice(0, numReadings);
    }
    // otherwise, pad the form out with empty entries
    else {
        const padding = numReadings - readings.length;
        for (let i = 0; i < padding; i++) {
            readings.push({
                reading: '',
                index: 0,
                unit: '',
                multiplier: 0,
                offset: 0
            })
        }
    }

    const onSubmit = (data: any) => {

        // Convert string types from the form into numbers
        // This should be handled by react-hook-form, see components/deviceconfig/index.tsx for explanation why it isn't
        if (data.bootup_time) data.bootup_time = parseInt(data.bootup_time);
        if (data.record_interval) data.record_interval = parseInt(data.record_interval);
        data.readings.forEach((reading: any, i: number) => {
            reading.index = parseInt(reading.index);
            reading.offset = parseFloat(reading.offset);
            reading.multiplier = parseFloat(reading.multiplier);
        })

        console.log(data)
        console.log(`sending data to ${process.env.API_URL}config/sdi12/${props.name}`)

        request({
            url: `${process.env.API_URL}config/sdi12/update/${props.name}`,
            method: "POST",
            body: JSON.stringify(data),
            init_message: "Updating sensor settings...",
            success_message: "Settings updated!",
            success_callback: () => getConfig()
        }, notyf);
    }

    const onRename = (name: string) => {
        request({
            url: `${process.env.API_URL}config/sdi12/rename/${props.name}`,
            method: "POST",
            body: JSON.stringify({name: name}),
            init_message: "Renaming sensor...",
            success_message: "Sensor updated!",
            success_callback: () => getConfig()
        }, notyf);
    }

    const onDelete = (data: any) => {
        request({
            url: `${process.env.API_URL}config/sdi12/delete/${props.name}`,
            method: "POST",
            init_message: "Deleting sensor...",
            success_message: "Sensor deleted!",
            success_callback: () => getConfig()
        }, notyf);
    }

    return (
        <div className={componentstyle.block}>
            <div className={componentstyle.header} onClick={() => setOpened(!opened)}>
                <span> {props.name}
                    <span style={{float: 'right'}}>
                        {opened ? <FaArrowUp/> : <FaArrowDown/>}
                    </span>
                </span>
            </div>

            <div
                className={opened ? componentstyle.opened : componentstyle.collapsed}
                ref={ref}
            >
                <div className={componentstyle.buttons}>
                <span className={componentstyle.buttonsList}>
                    <RenameModal
                        name={props.name}
                        callback={(name: string) => onRename(name)}
                    />
                    <button onClick={onDelete}><FaTrash/>Delete</button>
                    <NumSensorsModal
                        readings={props.sensor.readings.length}
                        callback={((num: number) => setNumReadings(num))}
                    />
                </span>
                    </div>
                <form
                    onSubmit={(handleSubmit(onSubmit) as any)}
                    className={style.aligned}
                    style={{padding: "10px"}}
                >
                    {/*Fix for issue #308*/}
                    <fieldset style={{minWidth: '0'}}>
                        <div className={style.alignGroup}>
                            <label htmlFor="aligned-name">Enabled</label>
                            <input type="checkbox"
                                   {...register("enabled")}
                            />
                        </div>
                        <div className={style.alignGroup}>
                            <label htmlFor="aligned-name">Address</label>
                            <input type="text"
                                   {...register("address")}
                            />
                        </div>
                        <div className={style.alignGroup}>
                            <label htmlFor="aligned-name">Bootup time (seconds)</label>
                            <input type="number" id="aligned-name"
                                   {...register("bootup_time")}
                            />
                        </div>
                        <div className={style.alignGroup}>
                            <label htmlFor="aligned-name">Record Interval (minutes)</label>
                            <input type="number" id="aligned-name"
                                   {...register("record_interval")}
                            />
                        </div>

                        {readings.map((reading, i) => (
                            <div>
                                <h4>Reading {i + 1}</h4>
                                <div className={style.alignGroup}>
                                    <label htmlFor="aligned-name">Name</label>
                                    <input type="text" id="aligned-name"
                                           name={`readings[${i}].reading`}
                                           {...register}
                                    />
                                </div>
                                <div className={style.alignGroup}>
                                    <label htmlFor="aligned-name">Index</label>
                                    <input type="number" id="aligned-name"
                                           name={`readings[${i}].index`}
                                           {...register}
                                    />
                                </div>
                                <div className={style.alignGroup}>
                                    <label htmlFor="aligned-name">Unit</label>
                                    <input type="text" id="aligned-name"
                                           name={`readings[${i}].unit`}
                                           {...register}
                                    />
                                </div>
                                <div className={style.alignGroup}>
                                    <label htmlFor="aligned-name">Multiplier (span)</label>
                                    <input type="number" id="aligned-name"
                                           name={`readings[${i}].multiplier`}
                                           {...register}
                                           step={"any"}
                                    />
                                </div>
                                <div className={style.alignGroup}>
                                    <label htmlFor="aligned-name">Offset (zero)</label>
                                    <input type="number" id="aligned-name"
                                           {...register}
                                           step={"any"}
                                    />
                                </div>
                            </div>
                        ))}
                        <TestOutput name={props.name}/>
                        <input type="submit"
                               value="Save Settings"
                               className={style.bigButton}
                               style={{
                                   fontSize: '18px',
                                   width: '49%',
                                   float: 'right'
                               }}/>
                    </fieldset>
                </form>
            </div>
        </div>
    );
}

export default ConfigureBlock;
