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
import { deviceConfigType } from "../interfaces";
import * as style from "../style.css";
import { useForm } from "react-hook-form";
import { ESP32_UNIX_EPOCH, formatDateTime, timestampToDate } from "../../util";
import { useContext } from "preact/hooks";
import { getNotyfContext } from "../../util/notyfContext";
import { fetchApiContext, request } from "../../util/apiClient";
import { useState } from 'preact/hooks';



const DeviceConfigPage: React.FunctionComponent<deviceConfigType> = (props) => {
    const {register, handleSubmit} = useForm<deviceConfigType>({
        defaultValues: {
            device_name: props.device_name,
            device_id: props.device_id,
            wifi_ssid: props.wifi_ssid,
            wifi_password: props.wifi_password,
            first_send_at_date: props.first_send_at_date,
            first_send_at_time: props.first_send_at_time,
            send_interval: props.send_interval
        }
    });

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

    // showPassword state here
    const [showPassword, setShowPassword] = useState(false);

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };



    return (
        <div className={style.page}>
            <h2>Device Settings</h2>

            <div>
                <form className={style.aligned} onSubmit={(handleSubmit(onSubmit) as any)}>
                    {/*<fieldset>*/}
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
                        <label htmlFor="aligned-name">Wifi SSID</label>
                        <input type="text"
                               className="aligned-name"
                               name="wifi_ssid"
                               ref={register}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Wifi Password</label>
                        <input type={showPassword ? 'text' : 'password'}
                               className="aligned-name"
                               name="wifi_password"
                               ref={register}
                        />
                        <button
                            type="button"
                            onClick={togglePasswordVisibility}
                            className={style.toggleButton}
                            >
                                {showPassword ? 'Hide' : 'Show'} Password
                            </button>
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">First Send At (Date)</label>
                        <input type={"date"}
                               className="aligned-name"
                               name="first_send_at_date"
                               ref={register}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">First Send At (Time)</label>
                        <input type={"time"}
                               className="aligned-name"
                               name="first_send_at_time"
                               ref={register}
                        />
                    </div>
                    <div className={style.alignGroup}>
                        <label htmlFor="aligned-name">Send Interval (mins) </label>
                        <input type="number"
                               className="aligned-name"
                               name="send_interval"
                               min={1}
                               ref={register}
                        />
                    </div>
                    {/*</fieldset>*/}
                    <input type="submit" value={"Save Device Settings"} className={style.bigButton}/>
                </form>
            </div>
        </div>
    )
};

export default DeviceConfigPage;
