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

import "preact/debug";
import {FunctionalComponent, h, PreactContext} from "preact";
import React, {useLayoutEffect, useState} from "react";
import {deviceDataType, deviceConfigType, deviceHistoryType} from "./interfaces";
import {useWindowSize} from "../util";
import * as style from './style.css'

import VisualisePage from "./visualise";
import DeviceConfigPage from "./deviceconfig";
import SensorConfigPage from "./sensorconfig";
import HistoryPage from "./history";
import Header from "./header";
import Tabs from "./tabs";
import MonitorPage from "./monitor";
import {useContext} from "preact/hooks";
import { getNotyfContext } from "../util/notyfContext";
import { FetchApiProvider } from "../util/apiClient";

import { Login } from "./security/login"
import { Register } from "./security/register"

// eslint-disable-next-line @typescript-eslint/no-explicit-any
if ((module as any).hot) {
    // tslint:disable-next-line:no-var-requires
    require("preact/debug");
}

const App: FunctionalComponent = () => {
    const mobileWidth = 768;
    const API_URL = process.env.API_URL;
    const LOADING_NOTICE = "loading...";

    const [currentTab, setCurrentTab] = React.useState(0);
    const [width, height] = useWindowSize();

    const [isLoggedIn, setLoggedIn] = useState(false);

    const notyf = getNotyfContext();

    // Set up side-effect hooks which get data from the webserver.
    const [deviceData, setDeviceData] = React.useState<deviceDataType>({
        last_transmitted: 0,
        last_updated: 0,
        messages_sent: 0,
        battery_level: 100,
        coverage_level: 100,
        failed_transmissions: 0,
        free_sd_space: 0,
    });

    const [deviceConfig, setDeviceConfig] = React.useState<deviceConfigType>({
        device_name: LOADING_NOTICE,
        device_id: LOADING_NOTICE,
        maintenance_mode: false,
        first_send_at_date: "",
        first_send_at_time: "",
        first_send_at: 0,
        send_interval: 0,
        wifi_ssid: "",
        wifi_password: "",
        sdi12_sensors: {}
    });

    const [deviceHistory, setDeviceHistory] = React.useState<deviceHistoryType>({
        graph_input: "",
        device_name: LOADING_NOTICE,
        device_id: LOADING_NOTICE,
        first_send_at_date: "",
        first_send_at_time: "",
        first_send_at: 0,
        last_send_at_date: "",
        last_send_at_time: "",
        last_send_at: 0,
        rain_gauge: LOADING_NOTICE,
        water_level: 50,
    });

    /**
     * Fetch Data from the API and set state
     */
    const fetchData = () => {
        fetch(`${API_URL}data`)
            .then(res => res.json())
            .then(res => setDeviceData(res))
            .catch(err => console.log(err));
    }

    /**
     * Fetch config from API and set state
     */
    const fetchConfig = () => {
        //  notify user
        notyf.open({type: 'info', message: 'Retrieving latest config...'})

        fetch(`${API_URL}config`)
            .then(res => res.json())
            .then(res => setDeviceConfig(res))
            .catch(err => console.log(err));
    }

    React.useEffect(() => {
        fetchConfig()
    }, []);
    React.useEffect(() => {
        fetchData()
    }, []);

    /**
     * Callback function from tabs that sets the currently active screen
     * @param tab
     */
    const tabClick = (tab: number) => {
        setCurrentTab(tab);
    };

    const tabs = [
        <VisualisePage {...deviceData}/>,
        // Don't render device config page until the data has loaded, because react-hook-form sets the defaults on only first render.
        // At first render, the device is still waiting for the API to return the config.
        // This is such a hacky workaround I'm sorry
        deviceConfig.device_name !== LOADING_NOTICE ? <DeviceConfigPage {...deviceConfig}/> : <div/>,
        <SensorConfigPage {...deviceConfig}/>,
        <HistoryPage {...deviceHistory}/>,
    ]

    // Add monitor as another tab if mobile size
    if (width < mobileWidth) {
        tabs.push(<MonitorPage/>)
    }
    // handle the edge case of resizing the screen if the current tab is the monitor.
    // just reset it back to the visualise screen if that happens.
    else if (currentTab == 4) {
        setCurrentTab(0);
    }

    if (!isLoggedIn) {
        return (
            <Login></Login>
        )
    }

    return (
        <FetchApiProvider value={fetchConfig}>
        <div id="app">
            <div className={style.topHeader}>
                <Header
                    deviceName={deviceConfig.device_name}
                    deviceID={deviceConfig.device_id}
                />
            </div>
            <Tabs click={tabClick} active={currentTab} fullscreen={width > mobileWidth}/>

            <div className={style.mainContent}>
                {/*Display left side if fullscreen, or current tab if mobile*/}
                <div className={style.col}>

                    { /*Rather than just rendering the active tab, every tab is rendered.
                        This is so that state is preserved if the user changes tab.
                        Implemented by setting 'display: none' on each component
                        * */}
                    {tabs.map((tab, i) => (
                        <VisibleWrapper active={currentTab === i} key={i} wrapped={tab}/>
                    ))}
                </div>

                {/*Always display monitor in widescreen mode*/}
                {width > mobileWidth ? (
                    <div className={style.col}>
                        <MonitorPage/>
                    </div>
                ) : null}
            </div>
        </div>
        </FetchApiProvider>
    );
};

/**
 * Wrapper element for a page.
 * props: active = whether or not to show the page
 *        wrapped = wrapped page
 * @constructor
 */
const VisibleWrapper = (props: { active: boolean, wrapped: any }) => (
    <div style={props.active ? undefined : {display: "none"}}>
        {props.wrapped}
    </div>
)

export default App;
