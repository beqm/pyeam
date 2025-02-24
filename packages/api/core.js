/** @type {Record<string, any>} */
const pendingResponses = {};


if (typeof window !== 'undefined' && window.chrome?.webview) {
    Object.defineProperty(window, 'nyvalis', {
        value: window.chrome.webview,
        writable: false,
        configurable: false,
        enumerable: false,
    });

}

function initializeWebViewListener() {
    if (!window.nyvalis) {
        console.warn("WebView not found");
        return;
    }

    window.nyvalis.addEventListener("message", /** @param {MessageEvent} event */(event) => {
        /** @type {{ id: string; data: any; error?: string }} */
        const payload = JSON.parse(event.data);
        const { id, data, error } = payload;

        if (error != null) {
            console.error(error);
        } else {
            pendingResponses[id] = data;
        }
    });
}

/**
 * Calls a invoke function from python
 * 
 * @param {string} command - name of the function
 * @param {Record<string, any>} params - Parameters
 * @returns {Promise<any>} - Promise with the python response
 */
export function invoke(command, params) {
    return new Promise((resolve) => {
        const requestId = crypto.randomUUID();

        window.nyvalis.postMessage({ command, params, id: requestId });

        const interval = setInterval(() => {
            if (pendingResponses[requestId] !== undefined) {
                clearInterval(interval);
                const response = pendingResponses[requestId];
                delete pendingResponses[requestId];
                resolve(response);
            }
        }, 10);
    });
}

if (typeof window !== 'undefined') {
    initializeWebViewListener();
}
