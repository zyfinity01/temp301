import { h } from 'preact';
import { useState } from 'preact/hooks';

export const Login = () => {
    const [username, setUsername] = useState('');
    const [pass, setPass] = useState('');

    const handleSubmit = () => {
        e.preventDefault(); // Prevent the page from reloading and loosing our state
        console.log(username);

    }

    return (
        <form onSubmit={handleSubmit}>
            <label for="username">Username:</label>
            <input value={username} type="username" placeholder="Enter username..." id="username" name="username"/>

            <label for="password">Password:</label>
            <input value={pass} type="password" placeholder="*******" id="password" name="password"/>

            <button>Log In</button>

        </form>
    )

}
