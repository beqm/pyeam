import "./App.css";
import { invoke } from '@nyvalis/api';
import React, { useState } from "react";

function App() {
    const [name, setName] = useState("");
    const [message, setMessage] = useState("");

    const example = async () => {
        const message = await invoke("example", { name });
        setMessage(message)
    };

    return (
        <main className="relative flex h-screen flex-col items-center justify-center overflow-hidden bg-gradient-to-b from-blue-200 to-white text-center font-sans">
            <img src="/logo.svg" class="w-32 h-32 mb-10" alt=""/>
            <h1 className="text-4xl text-[#4a5063]">Nyvalis</h1>
            <div className="mt-5 flex gap-4">
                <input
                    id="greet-input"
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="rounded-lg border-2 border-[#4a5063] bg-[#b0c4deaa] p-2 backdrop-blur-sm transition-colors outline-none focus:bg-[#8fa1bd]"
                />
                <button onClick={example} className="cursor-pointer rounded-lg bg-[#4a5063] p-2 px-4 text-lg text-white transition hover:bg-[#393e4d]">
                    Say Hello
                </button>
            </div>

            <p className="mt-5 text-lg text-[#393e4d]" style={{ visibility: message === "" ? "hidden" : "visible" }}>
                {message}
            </p>

            {[...Array(50)].map((_, i) => (
                <div
                    key={i}
                    className="animate-snowfall absolute top-0 rounded-full bg-white opacity-80"
                    style={{
                        left: `${Math.random() * 100}vw`,
                        animationDuration: `${Math.random() * 3 + 2}s`,
                        animationDelay: `-${Math.random() * 5}s`,
                        width: `${Math.random() * 5 + 5}px`,
                        height: `${Math.random() * 5 + 5}px`,
                    }}
                ></div>
            ))}
        </main>
    );
};

export default App;