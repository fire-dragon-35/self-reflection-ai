<script lang="ts">
  import { marked } from 'marked';
  
  marked.setOptions({
    breaks: true,
    gfm: true,
  });
  
  export let analysis: any;
  export let summary: string | null;
  export let analyzing: boolean;
  export let insightsError: string;
  export let onTriggerAnalysis: () => void;
  export let onClearError: () => void;
</script>

<div class="card h-[500px] sm:h-[600px] flex flex-col relative">
  <div class="flex items-center justify-between mb-6">
    <h2 class="text-xl font-semibold">Your Insights</h2>
    {#if analysis?.timestamp}
      <span class="text-xs text-gray-500">
        {new Date(analysis.timestamp).toLocaleDateString()}
      </span>
    {/if}
  </div>

  {#if insightsError}
    <div class="absolute top-16 left-4 right-4 bg-red-900/90 border border-red-800 rounded-lg p-3 z-20 animate-fade-in">
      <div class="flex items-start justify-between gap-2">
        <p class="text-sm text-red-400 flex-1">{insightsError}</p>
        <button 
          on:click={onClearError}
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
      <!-- Big Five Personality -->
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
                ></div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
      
      <!-- Thinking Patterns -->
      {#if analysis.thinking_patterns}
        <div class="mb-6">
          <h3 class="font-semibold mb-4">Thinking Patterns</h3>
          <div class="bg-[#1a1f2e] border border-gray-700 rounded-lg p-4 space-y-3">
            
            {#if analysis.thinking_patterns.cognitive_distortions && analysis.thinking_patterns.cognitive_distortions.length > 0}
              <div>
                <p class="text-xs text-gray-500 mb-2">Cognitive Distortions</p>
                <div class="flex flex-wrap gap-2">
                  {#each analysis.thinking_patterns.cognitive_distortions as distortion}
                    <span class="text-xs bg-gray-700 px-2 py-1 rounded">
                      {distortion.replace(/_/g, ' ')}
                    </span>
                  {/each}
                </div>
              </div>
            {/if}
            
            <div class="grid grid-cols-3 gap-3 text-center text-sm">
              <div>
                <p class="text-xs text-gray-500">Problem Solving</p>
                <p class="text-lg font-semibold">{analysis.thinking_patterns.problem_solving}/10</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Certainty</p>
                <p class="text-lg font-semibold">{analysis.thinking_patterns.certainty}/10</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Agency</p>
                <p class="text-lg font-semibold">{analysis.thinking_patterns.agency}/10</p>
              </div>
            </div>
          </div>
        </div>
      {/if}
      
      <!-- Communication Style -->
      {#if analysis.communication_style}
        <div class="mb-6">
          <h3 class="font-semibold mb-4">Communication Style</h3>
          <div class="bg-[#1a1f2e] border border-gray-700 rounded-lg p-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-400">Self-talk tone</span>
              <span class="capitalize">{analysis.communication_style.self_talk_tone}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-400">Emotional expression</span>
              <span class="capitalize">{analysis.communication_style.emotional_expression}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-400">Thought complexity</span>
              <span class="capitalize">{analysis.communication_style.thought_complexity}</span>
            </div>
          </div>
        </div>
      {/if}
      
      <!-- Summary -->
      {#if summary}
        <div>
          <h3 class="font-semibold mb-4">Summary</h3>
          <div class="bg-[#1a1f2e] border border-gray-700 rounded-lg p-4">
            <div class="prose prose-invert prose-sm max-w-none">
              {@html marked(summary)}
            </div>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  <div class="border-t border-gray-800 pt-4 mt-4">
    <button 
      on:click={onTriggerAnalysis} 
      disabled={analyzing}
      class="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg disabled:bg-gray-700 disabled:opacity-50"
    >
      {analyzing ? 'Analysing...' : 'Generate Analysis'}
    </button>
  </div>
</div>