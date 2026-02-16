<script lang="ts">
  import { useClerkContext } from 'svelte-clerk/client';
  import { onMount, afterUpdate } from 'svelte';
  import { getMessages, sendChat, getAnalysis, triggerAnalysisAPI, clearMessages, handleApiError } from './api';
  import { marked } from 'marked';
  
  const ctx = useClerkContext();
  
  marked.setOptions({
    breaks: true,
    gfm: true,
  });
  
  // Chat state
  let message = '';
  let messages: Array<{role: string, content: string}> = [];
  let loading = false;
  let clearing = false;
  let chatError = '';
  let messagesContainer: HTMLElement;
  
  // Insights state
  let analysis: any = null;
  let analyzing = false;
  let insightsError = '';
  
  afterUpdate(() => {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });
  
  onMount(async () => {
    const token = await ctx.session?.getToken();
    if (!token) return;
    
    messages = await getMessages(token);
    analysis = await getAnalysis(token);
  });
  
  async function sendMessage() {
    if (!message.trim() || loading) return;
    
    const userMessage = message;
    message = '';
    loading = true;
    chatError = '';
    
    messages = [...messages, { role: 'user', content: userMessage }];
    
    try {
      const token = await ctx.session?.getToken();
      const response = await sendChat(token, userMessage);
      messages = [...messages, { role: 'assistant', content: response }];
    } catch (err) {
      const apiError = handleApiError(err);
      chatError = apiError.message;
      messages = messages.slice(0, -1);
    } finally {
      loading = false;
    }
  }
  
  async function handleClearMessages() {
    if (!confirm('Are you sure you want to clear your chat history?')) return;
    
    clearing = true;
    chatError = '';
    try {
      const token = await ctx.session?.getToken();
      await clearMessages(token);
      messages = [];
    } catch (err) {
      const apiError = handleApiError(err);
      chatError = apiError.message;
    } finally {
      clearing = false;
    }
  }
  
  async function triggerAnalysis() {
    analyzing = true;
    insightsError = '';
    try {
      const token = await ctx.session?.getToken();
      analysis = await triggerAnalysisAPI(token);
    } catch (err) {
      const apiError = handleApiError(err);
      insightsError = apiError.message;
    } finally {
      analyzing = false;
    }
  }
</script>

<main class="max-w-7xl mx-auto p-6">
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
    <!-- Chat (2/3) -->
    <div class="lg:col-span-2">
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
            {#if chatError}
              <div class="bg-red-900/20 border border-red-800 rounded-lg p-3">
                <p class="text-sm text-red-400">{chatError}</p>
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
    </div>
    
    <!-- Insights (1/3) -->
    <div>
      <div class="card h-[600px] flex flex-col relative">
        <h2 class="text-xl font-semibold mb-6">Your Insights</h2>

        {#if insightsError}
          <div class="absolute top-16 left-4 right-4 bg-red-900/90 border border-red-800 rounded-lg p-3 z-20 animate-fade-in">
            <div class="flex items-start justify-between gap-2">
              <p class="text-sm text-red-400 flex-1">{insightsError}</p>
              <button 
                on:click={() => insightsError = ''}
                class="text-red-400 hover:text-red-300"
              >
                ✕
              </button>
            </div>
          </div>
        {/if}
        
        <div class="flex-1 overflow-y-auto scrollbar-hide">
          {#if !analysis}
            <p class="text-gray-400 text-sm">No analysis yet</p>
          {:else}
            {#if analysis.big_five_personality}
              <div class="mb-6">
                <h3 class="font-semibold mb-4">Big Five Personality</h3>
                {#each Object.entries(analysis.big_five_personality) as [trait, score]}
                  <div class="mb-3">
                    <div class="flex justify-between text-sm mb-1">
                      <span class="capitalize text-gray-300">{trait}</span>
                      <span class="text-gray-400">{score}/10</span>
                    </div>
                    <div class="w-full bg-gray-800 rounded-full h-2">
                      <div 
                        class="{score > 5 ? 'bg-blue-500' : 'bg-gray-600'} h-2 rounded-full" 
                        style="width: {score * 10}%"
                      />
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
            
            {#if analysis.attachment_style}
              <div>
                <h3 class="font-semibold mb-4">Attachment Style</h3>
                <div class="bg-[#1a1f2e] border border-gray-700 rounded-lg p-4">
                  <p class="font-semibold mb-2">{analysis.attachment_style.style}</p>
                  <p class="text-sm text-gray-400">Anxiety: {analysis.attachment_style.anxiety_score}/10</p>
                  <p class="text-sm text-gray-400">Avoidance: {analysis.attachment_style.avoidance_score}/10</p>
                </div>
              </div>
            {/if}
          {/if}
        </div>

        <div class="border-t border-gray-800 pt-4 mt-4">
          <button 
            on:click={triggerAnalysis} 
            disabled={analyzing}
            class="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:bg-gray-700 disabled:opacity-50"
          >
            {analyzing ? 'Analyzing...' : 'Generate Analysis'}
          </button>
        </div>
      </div>
    </div>
  </div>
</main>