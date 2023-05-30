import { h } from 'preact';
import { useState } from 'preact/hooks';

import * as style from './style.css'

export const Login = () => {
    const [username, setUsername] = useState('');
    const [pass, setPass] = useState('');

    const handleSubmit = () => {
        e.preventDefault(); // Prevent the page from reloading and loosing our state
        console.log(username);

    }

    return (
        <div className={style.wholePage}>
            <div className={style.loginContainter}>
            <form className={style.loginForm} onSubmit={handleSubmit}>
                <h1> Login </h1>
                <label htmlFor="username">Username:</label>
                <input value={username} type="username" placeholder="Enter username..." id="username" name="username"/>

                <label htmlFor="password">Password:</label>
                <input value={pass} type="password" placeholder="*******" id="password" name="password"/>

                <button>Log In</button>

            </form>
        </div>

        </div>

    )

}
