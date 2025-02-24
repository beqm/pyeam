<script>
	import { invoke } from '@nyvalis/api';

	let name = '';
	let message = '';

	async function example() {
		message = await invoke('example', { name });
	}
</script>

<main
	class="relative flex h-screen flex-col items-center justify-center overflow-hidden bg-gradient-to-b from-blue-200 to-white text-center font-sans"
>
	<img src="/logo.svg" class="w-32 h-32 mb-10" alt="">
	<h1 class="text-4xl text-[#4a5063]">Nyvalis</h1>
	<div class="mt-5 flex gap-4">
		<input
			id="greet-input"
			placeholder="Enter your name"
			bind:value={name}
			class="rounded-lg border-2 border-[#4a5063] bg-[#b0c4deaa] p-2 backdrop-blur-sm transition-colors outline-none focus:bg-[#8fa1bd]"
		/>
		<button
			on:click={example}
			class="cursor-pointer rounded-lg bg-[#4a5063] p-2 px-4 text-lg text-white transition hover:bg-[#393e4d]"
		>
			Say Hello
		</button>
	</div>

	<p class="mt-5 text-lg text-[#393e4d]" class:hidden={message == ''}>{message}</p>

	{#each Array(50) as _, i}
		<div
			class="animate-snowfall absolute top-0 rounded-full bg-white opacity-80"
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

<style>
	@keyframes snowfall {
		to {
			transform: translateY(100vh);
		}
	}

	.animate-snowfall {
		animation: snowfall linear infinite;
	}
</style>
