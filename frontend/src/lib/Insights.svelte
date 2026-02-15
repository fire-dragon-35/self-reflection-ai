<script lang="ts">
  import { useClerkContext } from 'svelte-clerk/client';
  import { onMount } from 'svelte';
  import { getAnalysis, triggerAnalysisAPI, handleApiError } from './api';
  
  const ctx = useClerkContext();
  
  let analysis: any = null;
  let analyzing = false;
  let error = '';
  
  onMount(async () => {
    const token = await ctx.session?.getToken();
    if (!token) return;
    
    analysis = await getAnalysis(token);
  });
  
  async function triggerAnalysis() {
    analyzing = true;
    error = '';
    try {
      const token = await ctx.session?.getToken();
      analysis = await triggerAnalysisAPI(token);
    } catch (err) {
      const apiError = handleApiError(err);
      error = apiError.message;
    } finally {
      analyzing = false;
    }
  }
</script>

<div class="card h-[600px] flex flex-col relative">
  <h2 class="text-xl font-semibold mb-6">Your Insights</h2>
  
  <!-- Error toast (fixed position, doesn't push content) -->
  {#if error}
    <div class="absolute top-16 left-4 right-4 bg-red-900/90 border border-red-800 rounded-lg p-3 z-20 animate-fade-in">
      <div class="flex items-start justify-between gap-2">
        <p class="text-sm text-red-400 flex-1">{error}</p>
        <button 
          on:click={() => error = ''}
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
  
  <!-- Generate Analysis button -->
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