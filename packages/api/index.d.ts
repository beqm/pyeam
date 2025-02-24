
declare module '@nyvalis/api' {

    interface NyvalisWebView {
      addEventListener(type: "message", listener: (event: MessageEvent) => void): void;
      postMessage(message: { command: string, params: Record<string, any>, id: string }): void;
    }
  
    interface Window {
      nyvalis?: NyvalisWebView;
    }
    
    function invoke(command: string, params: Record<string, any>): Promise<any>;
  
    export { invoke };
  }
  