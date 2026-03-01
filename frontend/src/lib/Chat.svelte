<script lang="ts">
  import { marked } from 'marked';
  import { afterUpdate } from 'svelte';
  
  marked.setOptions({
    breaks: true,
    gfm: true,
  });
  
  export let messages: Array<{role: string, content: string}>;
  export let message: string;
  export let loading: boolean;
  export let chatError: string;
  export let onSendMessage: () => void;
  export let onMessageChange: (value: string) => void;
  
  let messagesContainer: HTMLElement;
  
  afterUpdate(() => {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });
</script>

<div class="card h-[500px] sm:h-[600px] flex flex-col">
  <div class="flex-1 overflow-y-auto scrollbar-hide relative" bind:this={messagesContainer}>
    <div class="sticky top-0 h-8 bg-gradient-to-b from-[#151a21] via-[#151a21]/80 to-transparent pointer-events-none z-10"></div>
    
    <div class="p-4 space-y-4 -mt-8 pt-8">
      {#each messages as msg}
        <div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}">
          <div class="max-w-[80%] rounded-lg p-3 {msg.role === 'user' ? 'bg-blue-500' : 'bg-[#1a1f2e]'}">
            {#if msg.role === 'assistant'}
              <div class="prose prose-invert prose-sm max-w-none">
                {@html marked(msg.content)}
              </div>
            {:else}
              {msg.content}
            {/if}
          </div>
        </div>
      {/each}
      {#if loading}
        <div class="bg-[#1a1f2e] rounded-lg p-3 animate-pulse">Thinking...</div>
      {/if}
      {#if chatError}
        <div class="bg-red-900/20 border border-red-800 rounded-lg p-3">
          <p class="text-sm text-red-400">{chatError}</p>
        </div>
      {/if}
    </div>
  </div>
  
  <div class="border-t border-gray-800 p-4">
    <form on:submit|preventDefault={onSendMessage} class="flex gap-2">
      <input
        type="text"
        value={message}
        on:input={(e) => onMessageChange(e.currentTarget.value)}
        placeholder="What's on your mind?"
        class="input flex-1"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !message.trim()}
        class="btn-primary disabled:bg-gray-700 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </form>
  </div>
</div>