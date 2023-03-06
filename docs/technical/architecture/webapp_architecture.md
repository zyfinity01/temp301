# Web App Architecture

- [Web App Architecture](#web-app-architecture)
  - [Build Process](#build-process)
  - [Implementation of Architecture using Functional Components](#implementation-of-architecture-using-functional-components)
  - [Handling "Globally" Shared resources](#handling-globally-shared-resources)
  - [Implementation of User-feedback Notifications](#implementation-of-user-feedback-notifications)

The Web App is the primary way of configuring the device and calibrating the sensor readings.
This section discusses the architecture, build process and functional implementation of the frontend, built on the Preact framework.
For an outline of the requirements and decisions that went into the _web design_, see the [2020 Software Report](/docs/literature/Secker2020FinalReport.pdf).

At a high level, the _App_ component is the Web App entrypoint and top-most component, being rendered first by the browser
Once the entire pre-rendered static files have been loaded by the client, the app makes requests to the backend API endpoints `/config` and `/data`
These endpoints return JSON objects which represent the state of the entire application
The _App_ component passes the relevant information as "props" - read-only arbitrary inputs - to its child components
Each subcomponent contains code to render a UI component based on its internal state and its props.

<!-- TODO: Put in a DAG-style dependency graph -->

## Build Process

To turn the Web App source files and dependencies into a
production-ready Web App running on the microcontroller, an optimised
build process was configured.

The first stage in the build process checks for typescript errors.
[Typescript](https://www.typescriptlang.org/) is an extension to Javascript that adds static typing.
We explicitly enforce strict static typing for the entire project - every variable needs an explicitly defined type (or infers it).
For example, a portion of the global `interfaces.ts` file defines the types associated with the data returned by the backend API, shown in the following listing:

```typescript
export type SDISensorType = { address: string; bootup_time: number; enabled: boolean }
const sensor: SDISensorType = { address: 'A', bootup_time: 1, enabled: true }
```

In this example, the type `SDISensorType` concretely implements part of the device configuration defined [here](configuration.md).
This allows the programmer to create a new object, _sensor_, that implements this interface.
Defining this type enforces the primitive types (strings, numbers, booleans etc) of the properties of a sensor object, leading to less type errors, more resilient code and reducing development time.

The second stage _transpiles_ React code into native Javascript.
Transpiling is the process performed by the library [Babel](https://babeljs.io/) that allows modern code to be backwards compatible and support all browsers.
This process also involves injecting environment variables into the code.
Environment variables are used by the developer and Continuous Integration process  to differentiate between a development and production build.
In a development build, the Web App connects to a [webserver simulator backend](/software/simulator/src/README.md), whilst a production build uses the webserver on the microcontroller.
Environment variables enable this switch between contexts.

The third stage, performed by the [WebPack](https://webpack.js.org/) library, minifies and bundles the transpiled code into HTML, CSS and Javascript files.
Minification is a process that removes unnecessary or redundant data from the source code without changing the functionality - things like shortening variable names, removing formatting and comments, etc.
A further optimisation we perform on top of the webpack process is to compress the bundled files with _gzip_.
This has the effect of reducing the total file-size by around 50%.
This is performed in the [build.sh script](/software/device/build.sh).

## Implementation of Architecture using Functional Components

The structure of each component in the Web App follows a functional paradigm, where components are composed from literal javascript functions, for example:

```typescript
    const component: FunctionalComponent = (props: PropType) => {
        return <div>I am a component named {props.name}!</div>
    }
```

This design allows for strong composability and makes it easy to reason about the state of the component.
An interesting note is that the code above is not valid javascript - the return statement returns HTML directly.
This is a react-specific syntactic extension of javascript called JSX, that combines javascript and HTML into the same file.
Because the browser does not natively understand JSX, part of the compilation process "transpiles" this code into browser-readable javascript, as described above.

The ideal functional component is _"pure"_, containing no side effects or mutable state.
However, in a dynamic Web Application the state changes often - buttons are pressed, dropdowns toggled, and forms are modified.
This is accomplished in functional components with [React Hooks](https://reactjs.org/docs/hooks-intro.html), a feature of the React framework.
Hooks are a new feature of the library that offer ways to "attach" reusable behaviour to a component.

One such hook is the `useState()` hook.
These hooks allow reuse of state logic without changing the component hierarchy, letting components change their output over time in response to user actions, network responses and anything else without violating the functional rule.
For example, the _Monitor_ component needs to track mutable state to store whether or not it can send commands to the device.
This can be stored in the component with `const [canSend, setCanSend] = React.useState(true);` In this line, `useState(true)` declares a "state variable" with a default value of `true`.
The function returns a pair of variables - `canSend` represents the state, and `setCanSend` is a reference to a callback function used to mutate the state.

This pattern is used throughout the application almost every component
It has allowed for simpler code that is easier to reason about and debug, and the functional design matches the design decisions of the device software.

## Handling "Globally" Shared resources

One problem faced with the architecture of the Web Application is globally-accessible state.
Most of the dynamic data in the application comes from the top layer _App_ component, which calls the backend API and passes the device data as props to subcomponents.
This relation is one-way, and props are read-only.
What happens if a sub-component, such as one that updates the device configuration, wants to update the top-level config object, so that the page doesn't have to be refreshed every time the onfiguration changes?
To ensure two-way communication back to the top component, the top-layer _update API_ method would need to be passed down to every component through props, leading to the well known and hard-to-maintain "callback hell".

To get around this problem, react provides another type of hook - `useContext()`.
A _context_ is an object with two values - a Provider and a Consumer, created with a library function `createContext()`.
the `useContext()` hook takes a context as an argument and returns the _context value_ for that context.
The value is determined by a specific prop - `value` - from the first Provider that sits above the the calling component in the tree.

In our app, we wrap the top layer `App` component in a context Provider, passing the `fetchConfig()` method - the method that retrieves the latest config from the webserver - into the provider as the _value_ argument.
Subcomponents that want to use the context now only have to call `useContext(fetchApiContext)`, which returns the callback function that updates the configuration data.
Now, every sub-component can be responsible for refreshing the applications global state.

## Implementation of User-feedback Notifications

The library [Notyf](https://www.npmjs.com/package/notyf) is used to implement notifications that display informational, success and error messages to the user. Notifications were implemented to provide a standard way of giving feedback to actions that hit the backend API in a centralised place. Furthermore, because API calls often took multiple seconds to run on the microcontroller, a message-based system helps assure the user that _something_ is happening.

Global notifications were implemented using the same `useContext()` hooks discussed earlier. An interesting issue was that the library caused the compiler to throw errors in the production build process, halting the compilation. This is because the library relies on the DOM, which is only available in the browser. Pre-rendering runs in Node, which has no access to browser APIs. To get around this, a mock Notyf context was implemented that overrides the notification methods with empty stubs. A higher-order function was implemented to wrap the `useContext()` method, returning the actual Notyf context if the DOM is accessible, or the mock context otherwise.

Relevant code: [`software/device/webapp/src/util/notyfContext.ts`](/software/device/webapp/src/util/notyfContext.ts)
