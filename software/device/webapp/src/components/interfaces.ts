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

export type deviceDataType = {
    last_transmitted: number;
    last_updated: number;
    messages_sent: number;
    battery_level: number;
    coverage_level: number;
    failed_transmissions: number;
    free_sd_space: number;
}

export type deviceConfigType = {
    device_name: string;
    device_id: string;
    wifi_ssid: string;
    wifi_password: string;
    send_interval: number;

    // Store date+time as string in frontend
    first_send_at_date: string;
    first_send_at_time: string;
    first_send_at: number;

    maintenance_mode: boolean;
    sdi12_sensors: {
        [key: string]: SDISensorType
    };
}

// For History Tab - first edition, need to update these values at a later date, inputs relate to the history/index.ts page
export type deviceHistoryType = {
    graph_input: string;
    device_name: string;
    device_id: string;
    rain_gauge: string;
    water_level: number;

    // Store date+time as string in frontend
    first_send_at_date: string;
    first_send_at_time: string;
    first_send_at: number;

    last_send_at_date: string;
    last_send_at_time: string;
    last_send_at: number;
}

export type SDISensorType = {
    // TODO number/string discussion in #161
    address: string;
    bootup_time: number;
    record_interval: number;
    enabled: boolean;
    readings: {
        reading: string;
        index: number;
        unit: string;
        multiplier: number;
        offset: number;
    }[];
}

export interface SDIMessageType {
    response: string;
    command: string;
    error?: string;
}
