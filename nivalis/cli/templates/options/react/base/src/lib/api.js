/** @type {Record<string, any>} */
const pendingResponses = {};

/**
 * Inicializa o listener para receber mensagens do WebView.
 */
export function initializeWebViewListener() {
    if (!window.chrome?.webview) {
        console.warn("WebView não encontrado");
        return;
    }

    window.chrome.webview.addEventListener("message", /** @param {MessageEvent} event */(event) => {
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
 * Invoca um comando no backend via WebView e aguarda a resposta.
 * 
 * @param {string} command - O comando a ser executado.
 * @param {Record<string, any>} params - Os parâmetros para o comando.
 * @returns {Promise<any>} - Uma promessa que resolve com a resposta do backend.
 */
export function invoke(command, params) {
    return new Promise((resolve) => {
        const requestId = crypto.randomUUID();

        window.chrome.webview.postMessage({ command, params, id: requestId });

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
