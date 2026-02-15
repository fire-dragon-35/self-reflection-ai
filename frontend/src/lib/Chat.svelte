<script lang="ts">
  import { useClerkContext } from 'svelte-clerk/client';
  import { onMount, afterUpdate } from 'svelte';
  import { getMessages, sendChat, handleApiError, clearMessages } from './api';
  import { marked } from 'marked';
  
  const ctx = useClerkContext();
  
  // Configure marked for clean formatting
  marked.setOptions({
    breaks: true,
    gfm: true,
  });
  
  let message = '';
  let messages: Array<{role: string, content: string}> = [];
  let loading = false;
  let clearing = false;
  let error = '';
  let messagesContainer: HTMLElement;
  
  afterUpdate(() => {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });
  
  onMount(async () => {
    const token = await ctx.session?.getToken();
    if (!token) return;
    
    messages = await getMessages(token);
  });
  
  async function sendMessage() {
    if (!message.trim() || loading) return;
    
    const userMessage = message;
    message = '';
    loading = true;
    error = '';
    
    messages = [...messages, { role: 'user', content: userMessage }];
    
    try {
      const token = await ctx.session?.getToken();
      const response = await sendChat(token, userMessage);
      messages = [...messages, { role: 'assistant', content: response }];
    } catch (err) {
      const apiError = handleApiError(err);
      error = apiError.message;
      messages = messages.slice(0, -1);
    } finally {
      loading = false;
    }
  }
  
  async function handleClearMessages() {
    if (!confirm('Are you sure you want to clear your chat history?')) return;
    
    clearing = true;
    error = '';
    try {
      const token = await ctx.session?.getToken();
      await clearMessages(token);
      messages = [];
    } catch (err) {
      const apiError = handleApiError(err);
      error = apiError.message;
    } finally {
      clearing = false;
    }
  }
</script>

<div class="card h-[600px] flex flex-col">
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
      {#if error}
        <div class="bg-red-900/20 border border-red-800 rounded-lg p-3">
          <p class="text-sm text-red-400">{error}</p>
        </div>
      {/if}
    </div>
  </div>
  
  <div class="border-t border-gray-800 p-4 space-y-2">
    <form on:submit|preventDefault={sendMessage} class="flex gap-2">
      <input
        type="text"
        bind:value={message}
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
    <button
      on:click={handleClearMessages}
      disabled={clearing || messages.length === 0}
      class="w-full px-4 py-1.5 bg-gray-700/50 hover:bg-gray-600/50 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {clearing ? 'Clearing...' : 'Clear History'}
    </button>
  </div>
</div>