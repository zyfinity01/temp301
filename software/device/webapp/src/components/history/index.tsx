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
import { deviceHistoryType } from "../interfaces";
import * as style from "../style.css";
import * as style2 from "./style.css";
import { useForm } from "react-hook-form";
import { ESP32_UNIX_EPOCH } from "../../util";
import Popup from 'reactjs-popup';
import 'reactjs-popup/dist/index.css';

import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const options = {
    responsive: true,
    plugins: {
        legend: {
            position: 'top' as const
        },
        title: {
            display: true,
            text: 'Rainfall Data'
        }
    },
    scales: {
        x: {
            title: {
                display: true,
                text: 'Date (DD/MM/YY)'
            }
        },
        y: {
            title: {
                display: true,
                text: 'Rainfall (mm)'
            }
        }
    }
};

const labels = ['08/05/23', '09/05/23', '10/05/23', '11/05/23', '12/05/23', '13/05/23', '14/05/23'];

const data = {
    labels,
    datasets: [
        {
            label: 'Rainfall Data',
            data: [6, 1.5, 3, 0, 2, 1, 7],
            backgroundColor: 'rgb(135, 201, 198, 0.5)',
        }
    ]
};

const HistoryPage: React.FunctionComponent<deviceHistoryType> = (props) => {
    const {register, handleSubmit} = useForm<deviceHistoryType>({
        defaultValues: {
            graph_input: props.graph_input,
            device_name: props.device_name,
            device_id: props.device_id,
            rain_gauge: props.rain_gauge,
            water_level: props.water_level,
            first_send_at_date: props.first_send_at_date,
            first_send_at_time: props.first_send_at_time,
            first_send_at: props.first_send_at,
            last_send_at_date: props.last_send_at_date,
            last_send_at_time: props.last_send_at_time,
            last_send_at: props.last_send_at
        }
    });

    /**
     * Submit updated device configuration
     */
    const onSubmit = (data: any) => {

        // Convert date and time string into unix time, offset by MCU epoch
        if (data.first_send_at_time !== '' && data.first_send_at_date !== '') {
            const timestamp = Date.parse(`${data.first_send_at_date}T${data.first_send_at_time}`) - ESP32_UNIX_EPOCH

            // strip datetime data from form object, and add timestamp
            delete data.first_send_at_date
            delete data.first_send_at_time
            data.first_send_at = timestamp
        }

        if (data.last_send_at_time !== '' && data.last_send_at_date !== '') {
            const timestamp = Date.parse(`${data.last_send_at_date}T${data.last_send_at_time}`) - ESP32_UNIX_EPOCH

            // strip datetime data from form object, and add timestamp
            delete data.last_send_at_date
            delete data.last_send_at_time
            data.last_send_at = timestamp
        }
    }

    return (
        <div className={style.page}>
            <h2>Water Level History</h2>

            <div className={style2.graph}>
                <Bar options={options} data={data} />
            </div>

            <div>
                <form className={style.aligned} onSubmit={(handleSubmit(onSubmit) as any)}>
                    {/*<fieldset>*/}
                    <Popup
                        trigger={<button className={style.bigButton}>Filter</button>}
                        modal
                        contentStyle={{width: "21em", borderRadius: "5px", padding: "15px"}}
                    >
                    {
                        (close : any) => (
                            <div className='modal'>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">Start Date</label>
                                    <input type={"date"}
                                        className="aligned-name"
                                        {...register("first_send_at_date")}
                                    />
                                </div>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">End Date</label>
                                    <input type={"date"}
                                        className="aligned-name"
                                        {...register("last_send_at_date")}
                                    />
                                </div>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">Start Time</label>
                                    <input type={"time"}
                                        className="aligned-name"
                                        {...register("first_send_at_time")}
                                    />
                                </div>
                                <div className={style2.filter}>
                                    <label htmlFor="aligned-name">End Time</label>
                                    <input type={"time"}
                                        className="aligned-name"
                                        {...register("last_send_at_time")}
                                    />
                                </div>
                                <div>
                                    <button className={style2.bigButton} onClick={() => close()}>
                                        Apply
                                    </button>
                                </div>
                            </div>
                        )
                    }
                    </Popup>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Graph Display</label>
                        <select name = "graph_inputs" id = "inputs">
                            <option value = "precipitation_data">Precipitation</option>
                            <option value = "temp_data">Temperature</option>
                        </select>
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Device Name</label>
                        <input type="text"
                               className="aligned-name"
                               {...register("device_name")}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Device ID</label>
                        <input type="text"
                               className="aligned-name"
                               {...register("device_id")}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Rain Gauge</label>
                        <input type="text"
                               className="aligned-name"
                               {...register("rain_gauge")}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Water Level</label>
                        <input type="text"
                               className="aligned-name"
                               {...register("water_level")}
                        />
                    </div>
                </form>
            </div>
        </div>
    )
};

export default HistoryPage;
