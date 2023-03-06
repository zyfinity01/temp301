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

import {Notyf} from 'notyf';
import {createContext, PreactContext} from "preact";
import {useContext} from "preact/hooks";
import notyf from "notyf/notyf";

const notyfContextCreator = () => {
    // return (typeof window !== "undefined") ?
    return createContext(
        new Notyf({
            duration: 5000, // Set your global Notyf configuration here
            position: {
                x: "right",
                y: "top"
            },
            types: [
                {
                    type: 'info',
                    background: '#e7bb41',
                    dismissible: true,
                },
                {
                    type: 'success',
                    background: '#4b8b30',
                    dismissible: true,
                },
                {
                    type: 'error',
                    background: '#ff2222',
                    dismissible: true,
                }
            ]
        })
    )
// : createContext(NotyfStub)
}

/**
 * A hacky mock class for Notyf so that React pre-rendering doesn't pack a sad.
 * The Notyf lib throws errors in the production build process if pre-rendering is enabled.
 * See https://github.com/caroso1222/notyf/issues/67
 */
export class MockNotyfContext {
    info = (opts: any) => {}
    success = (opts: any) => {}
    error = (opts: any) => {}
    open = (opts: any) => {}
}

let notyfContext: any;
try {
    notyfContext = notyfContextCreator();
}
catch (e) {
    notyfContext = new MockNotyfContext();
}

export const getNotyfContext: any = () => {
    return useContext(notyfContext);
}
