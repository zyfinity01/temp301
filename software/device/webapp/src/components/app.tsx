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
import React, {useState, useEffect} from "react";
import {deviceDataType, deviceConfigType, deviceHistoryType} from "./interfaces";
import {useWindowSize} from "../util";
import * as style from './style.css';

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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
if ((module as any).hot) {
    // tslint:disable-next-line:no-var-requires
    require("preact/debug");
}

// Moved constants outside the component
const mobileWidth = 768;
const API_URL = process.env.API_URL;
const LOADING_NOTICE = "loading...";

// Moved API calls to separate functions
async function fetchDeviceData() {
    const res = await fetch(`${API_URL}data`);
    return res.json();
}

async function fetchDeviceConfig() {
    const res = await fetch(`${API_URL}config`);
    return res.json();
}

const App: FunctionalComponent = () => {
    const [currentTab, setCurrentTab] = React.useState(0);
    const [width, height] = useWindowSize();
    const notyf = getNotyfContext();
    const [loading, setLoading] = useState(true); // Added a loading state

    const [deviceData, setDeviceData] = React.useState<deviceDataType>({
        last_transmitted: 0,
        last_updated: 0,
        messages_sent: 0,
        battery_level: 100,
        coverage_level: 100,
        failed_transmissions: 0,
        free_sd_space: 0,
        rainfall: [],
        date_time: []
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


    useEffect(() => {
        async function fetchDataAndConfig() {
            notyf.open({type: 'info', message: 'Retrieving latest config...'});

            const dataPromise = fetchDeviceData()
                .then(data => {
                    setDeviceData(data);
                });

            const configPromise = fetchDeviceConfig()
                .then(config => {
                    setDeviceConfig(config);
                });

            await Promise.all([dataPromise, configPromise]);

            setLoading(false);
        }

        fetchDataAndConfig();
    }, []);


    const tabClick = (tab: number) => {
        setCurrentTab(tab);
    };

    const tabs = [
        <VisualisePage {...deviceData}/>,
        deviceConfig.device_name !== LOADING_NOTICE ? <DeviceConfigPage {...deviceConfig}/> : <div/>,
        <SensorConfigPage {...deviceConfig}/>,
        <HistoryPage {...deviceHistory}/>,
    ];


    if (width < mobileWidth) {
        tabs.push(<MonitorPage/>)
    } else if (currentTab === 4) {
        setCurrentTab(0);
    }

    return (
        <FetchApiProvider value={fetchDeviceConfig}>
        {loading ? <div>Loading...</div> : (
            <div id="app">
                <div className={style.topHeader}>
                    <Header
                        deviceName={deviceConfig.device_name}
                        deviceID={deviceConfig.device_id}
                    />
                </div>
                <Tabs click={tabClick} active={currentTab} fullscreen={width > mobileWidth}/>
                <div className={style.mainContent}>
                    <div className={style.col}>
                        {tabs.map((tab, i) => (
                            <VisibleWrapper active={currentTab === i} key={i} wrapped={tab}/>
                        ))}
                    </div>
                    {width > mobileWidth ? (
                        <div className={style.col}>
                            <MonitorPage/>
                        </div>
                    ) : null}
                </div>
            </div>
        )}
        </FetchApiProvider>
    );
};

const VisibleWrapper = (props: { active: boolean, wrapped: any }) => (
    <div style={props.active ? undefined : {display: "none"}}>
        {props.wrapped}
    </div>
)

export default App;
