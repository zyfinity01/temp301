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
import {deviceHistoryType, deviceDataType, SDISensorType} from "../interfaces";
import * as style from "../style.css";
import * as style2 from "./style.css";
import {useForm} from "react-hook-form";
import {ESP32_UNIX_EPOCH, formatDateTime, timestampToDate} from "../../util";
import {useContext} from "preact/hooks";
import { getNotyfContext } from "../../util/notyfContext";
import {fetchApiContext, request} from "../../util/apiClient";
import Popup from 'reactjs-popup';
import React from 'react';
// import {
//     Chart as ChartJS,
//     CategoryScale,
//     LinearScale,
//     BarElement,
//     Title,
//     Tooltip,
//     Legend
// } from "chart.js";
// import { Bar } from "react-chartjs-2";

// ChartJS.register(
//     CategoryScale,
//     LinearScale,
//     BarElement,
//     Title,
//     Tooltip,
//     Legend
// );

// const options = {
//     responsive: true,
//     plugins: {
//         legend: {
//             position: 'top' as const
//         },
//         title: {
//             display: true,
//             text: 'Rainfall Data'
//         }
//     },
//     scales: {
//         x: {
//             title: {
//                 display: true,
//                 text: 'Date (DD/MM/YY)'
//             }
//         },
//         y: {
//             title: {
//                 display: true,
//                 text: 'Rainfall (mm)'
//             }
//         }
//     }
// };

const labels = ['08/05/23', '09/05/23', '10/05/23', '11/05/23', '12/05/23', '13/05/23', '14/05/23'];

const data = {
    labels,
    datasets: [
        {
            label: 'Rainfall Data',
            data: [6, 1.5, 3, 0, 2, 1, 7],
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
        }
    ]
};

const HistoryPage: React.FunctionComponent<deviceHistoryType> = (props) => {
    const {register, handleSubmit, watch, reset} = useForm<deviceHistoryType>({
        defaultValues: {
            device_name: props.device_name,
            device_id: props.device_id,
            rain_gauge: props.rain_gauge,
            water_level: props.water_level,
            first_send_at_date: props.first_send_at_date,
            first_send_at_time: props.first_send_at_time,
            last_send_at_date: props.last_send_at_date,
            last_send_at_time: props.last_send_at_time,
        }
    });

    // Convert the esp32-offset unix timestamp into a string-formatted date and time string
    const first_send_at = timestampToDate(props.first_send_at);
    const [first_send_at_date, first_send_at_time] = formatDateTime(first_send_at);

    const last_send_at = timestampToDate(props.last_send_at);
    //The whole webpage goes blank when the following added, need to look into it.
    // const [last_send_at_date, last_send_at_time] = formatDateTime(last_send_at);

    const notyf = getNotyfContext();
    const getConfig = useContext(fetchApiContext);

    /**
     * Submit updated device configuration
     */
    const onSubmit = (data: any) => {

        // Convert date and time string into unix time, offset by MCU epoch
        if (data.first_send_at !== '' && data.first_send_at_date !== '') {
            const timestamp = Date.parse(`${data.first_send_at_date}T${data.first_send_at_time}`) - ESP32_UNIX_EPOCH

            // strip datetime data from form object, and add timestamp
            delete data.first_send_at_date
            delete data.first_send_at_time
            data.first_send_at = timestamp
        }

        if (data.last_send_at !== '' && data.last_send_at_date !== '') {
            const timestamp = Date.parse(`${data.last_send_at_date}T${data.last_send_at_time}`) - ESP32_UNIX_EPOCH

            // strip datetime data from form object, and add timestamp
            delete data.last_send_at_date
            delete data.last_send_at_time
            data.last_send_at = timestamp
        }

        // convert other fields to numbers.
        // This should be handled by react-hook-form, but it requires a bit of hacking with Controller components
        // https://github.com/react-hook-form/react-hook-form/issues/1414
        // https://codesandbox.io/s/react-hook-form-parse-and-format-textarea-furtc?file=/src/index.tsx
        if (data.send_interval) data.send_interval = parseInt(data.send_interval);

        console.log(data)
        console.log(`sending data to ${process.env.API_URL}config`)

        request({
            url: `${process.env.API_URL}config`,
            method: "POST",
            body: JSON.stringify(data),
            init_message: "Updating device data...",
            success_message: "Settings updated!",
            success_callback: () => getConfig()
        }, notyf);
    }

    return (
        <div className={style.page}>
            <h2>Water Level History</h2>

            {/* <div className={style2.graph}>
                <Bar options={options} data={data} />
            </div> */}

            <div>
                <form className={style.aligned} onSubmit={(handleSubmit(onSubmit) as any)}>
                    {/*<fieldset>*/}
                    <Popup trigger = {<button className={style.bigButton}>Filter</button>} modal>
                    {
                        close => (
                            <div className='modal'>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">Start Date</label>
                                    <input type={"date"}
                                        className="aligned-name"
                                        name="first_send_at_date"
                                        ref={register}
                                    />
                                </div>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">End Date</label>
                                    <input type={"date"}
                                        className="aligned-name"
                                        name="last_send_at_date"
                                        ref={register}
                                    />
                                </div>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">Start Time</label>
                                    <input type={"time"}
                                        className="aligned-name"
                                        name="first_send_at_time"
                                        ref={register}
                                    />
                                </div>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">End Time</label>
                                    <input type={"time"}
                                        className="aligned-name"
                                        name="last_send_at_time"
                                        ref={register}
                                    />
                                </div>
                                <div>
                                    <button className={style.bigButton} onClick={() => close()}>
                                        Apply
                                    </button>
                                </div>
                            </div>
                        )
                    }
                    </Popup>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Device Name</label>
                        <input type="text"
                               className="aligned-name"
                               name="device_name"
                               ref={register}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Device ID</label>
                        <input type="text"
                               className="aligned-name"
                               name="device_id"
                               ref={register}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Rain Gauge</label>
                        <input type="text"
                               className="aligned-name"
                               name="rain_gauge"
                               ref={register}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Water Level</label>
                        <input type="text"
                               className="aligned-name"
                               name="water_level"
                               ref={register}
                        />
                    </div>
                </form>
            </div>
        </div>
    )
};

// CSS stolen from bootstrap "well" component
const MessagesSentStyle = {
    "minHeight": "20px",
    "padding": "19px",
    "marginBottom": "20px",
    "backgroundColor": "#f5f5f5",
    "border": "1px solid #e3e3e3",
    "borderRadius": "4px",
    "WebkitBoxShadow": "inset 0 1px 1px rgba(0,0,0,.05)",
    "boxShadow": "inset 0 1px 1px rgba(0,0,0,.05)"
};

export default HistoryPage;
