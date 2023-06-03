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

import { createContext } from "preact";
import { MockNotyfContext } from "./notyfContext";
import { Notyf } from "notyf";

export const fetchApiContext = createContext(
    () => {}
);

export const FetchApiProvider = fetchApiContext.Provider;

interface requestOptions {
    url: string;
    init_message?: string;
    success_message?: string;
    method?: string;
    body?: any;
    success_callback?: ()=>void;
}

/**
 * Async function to create a request to the backend and return the response
 * If init_message and/or success_message params are set in opts, generates a
 * notification before and after the request respectively.
 * Also calls an optional callback on success.
 *
 * @param opts - request options
 * @param notyf - notification object
 */
export const request = async (opts: requestOptions, notyf: Notyf|MockNotyfContext) => {
    if (opts.init_message !== undefined) {
        console.log(opts)
        notyf.open({
            type: "info",
            message: opts.init_message
        });
    }

    try {

        const response = await fetch(opts.url, {
            method: opts.method,
            credentials: "same-origin",
            headers: opts.body !== undefined ? { "Content-Type": "application/json"}: undefined,
            body: opts.body
        });

        if (response.ok) {
            // Notify user
            if (opts.success_message !== undefined) {
                notyf.success(opts.success_message);
            }
            else {
                notyf.success("Request succeeded!")
            }
            if (opts.success_callback !== undefined)
                opts.success_callback();
            return await response.json();
        }

        else {
            const data = await response.json();
            notyf.error("error: " + data['error']);
            return data;
        }

    }
    catch (error) {
        notyf.error("error: " + error);
    }
}
