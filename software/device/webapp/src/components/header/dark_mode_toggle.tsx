import { h, FunctionComponent } from 'preact';
import { useEffect, useState } from 'preact/hooks';
import React from 'react';
import * as styleSheet from '../style.css';

// ThemeToggle component
const ThemeToggle: FunctionComponent = () => {
    // Function to retrieve the theme from localStorage or default to 0
    const getCurrTheme = () => {
        if (typeof window !== "undefined") {
            return localStorage.getItem('stored_theme') || '0';
        }
        return '0';
    }

    // State hook to manage the theme state
    const [theme, setTheme] = useState(getCurrTheme());

    let root: Element | null = null;

    // Assign the root element if the code is running in a browser environment
    if (typeof window !== "undefined") {
        root = document.querySelector(':root');
    }

    // Effect hook to update the theme in localStorage and set the colour-theme attribute on the root element
    useEffect(() => {
        if (typeof window !== "undefined") {
            localStorage.setItem('stored_theme', theme.toString());
        }
        document.documentElement.setAttribute('colour-theme', theme === '1' ? 'dark' : 'light');
    }, [theme]);

    // Function to toggle the theme
    const toggleTheme = (): void => {
        setTheme(theme === '1' ? '0' : '1');
    }

    const themeText = theme === '1' ? 'light' : 'dark';

    // Rendered JSX
    return (
        <div className={styleSheet.switchTheme} onClick={toggleTheme}>
            Switch to {themeText} Mode
        </div>
    )
}

export default ThemeToggle;
