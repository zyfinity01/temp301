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

import { useLayoutEffect, useState } from "preact/hooks";

/**
 * UTC timestamp of the ESP32 epoch (2020-01-01T12:00:00)
 */
export const ESP32_UNIX_EPOCH = 946684800000

const dateTimeFormat = new Intl.DateTimeFormat('en', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: 'numeric',
    hour12: false,
    minute: 'numeric',
    second: 'numeric'
});

/**
 * Function to get the size of the window, which is useful for dynamic rending
 */
export function useWindowSize() {
    const [size, setSize] = useState([0, 0]);
    useLayoutEffect(() => {
        function updateSize() {
            setSize([window.innerWidth, window.innerHeight]);
        }

        window.addEventListener('resize', updateSize);
        updateSize();
        return () => window.removeEventListener('resize', updateSize);
    }, []);

    return size;
}


/**
 * Return a formatted string for date and for time, given a date object.
 */
export function formatDateTime(dateObject: Date) {
    // format the date object, removing literals (date/time delimiters)
    const data = dateTimeFormat.formatToParts(dateObject)
        .filter(entry => entry.type !== 'literal')
        // map to more usable object: from {type: 'month', value:'01'} to {month: '01}
        .map(entry => {
            return {[entry.type]: entry.value}
        })
        // reduce to a singular object
        .reduce((l, r) => Object.assign(l, r), {})

    const dateString = `${data.year}-${data.month}-${data.day}`;
    const timeString = `${data.hour}:${data.minute}`;

    return [dateString, timeString];
}

/**
 * @return the ESP32 timestamp converted to a date object
 * @param timestamp in UNIX time with the ESP32 epoch offset
 */
export function timestampToDate(timestamp: number): Date {
    return new Date(timestamp + ESP32_UNIX_EPOCH);
}
