<script>
    import { invoke } from "$lib/api.js";

    let name = "";
    let message = "";

    async function example() {
        message = await invoke("example", { name });
    }
</script>

<main>
    <h1>Nivalis</h1>
    <div class="input-container">
        <input
            id="greet-input"
            placeholder="Enter your name"
            bind:value={name}
            class="input-field"
        />
        <button on:click={example} class="btn">Say Hello</button>
    </div>

    <p
        class="message"
        style={message == "" ? "visibility: hidden;" : "visibility: show;"}
    >
        {message}
    </p>

    {#each Array(50) as _, i}
        <div
            class="snowflake"
            style="
            left: {Math.random() * 100}vw;
            animation-duration: {Math.random() * 3 + 2}s;
            animation-delay: {-Math.random() * 5}s;
            width: {Math.random() * 5 + 5}px;
            height: {Math.random() * 5 + 5}px;
        "
        ></div>
    {/each}
</main>
