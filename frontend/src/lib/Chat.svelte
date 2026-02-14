<script lang="ts">
  import { useClerkContext } from 'svelte-clerk/client';
  import axios from 'axios';
  
  const ctx = useClerkContext();
  const API_URL = import.meta.env.VITE_API_URL;
  
  let message = '';
  let messages: Array<{role: string, content: string}> = [];
  let loading = false;
  
  async function sendMessage() {
    if (!message.trim() || loading) return;
    
    const userMessage = message;
    message = '';
    loading = true;
    
    messages = [...messages, { role: 'user', content: userMessage }];
    
    try {
      const token = await ctx.session.getToken();
      
      const response = await axios.post(
        `${API_URL}/api/chat`,
        { message: userMessage },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      messages = [...messages, { role: 'assistant', content: response.data.response }];
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to send message');
    } finally {
      loading = false;
    }
  }
</script>

<div class="bg-white rounded-lg shadow-lg h-[600px] flex flex-col">
  <div class="flex-1 overflow-y-auto p-4 space-y-4">
    {#each messages as msg}
      <div class="flex {msg.role === 'user' ? 'justify-end' : 'justify-start'}">
        <div class="max-w-[80%] rounded-lg p-3 {msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100'}">
          {msg.content}
        </div>
      </div>
    {/each}
    
    {#if loading}
      <div class="flex justify-start">
        <div class="bg-gray-100 rounded-lg p-3 animate-pulse">Thinking...</div>
      </div>
    {/if}
  </div>
  
  <div class="border-t p-4">
    <form on:submit|preventDefault={sendMessage} class="flex gap-2">
      <input
        type="text"
        bind:value={message}
        placeholder="What's on your mind?"
        class="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !message.trim()}
        class="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
      >
        Send
      </button>
    </form>
  </div>
</div>