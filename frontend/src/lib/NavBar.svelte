<script lang="ts">
  import { useClerkContext, UserButton } from 'svelte-clerk/client';
  import { onMount } from 'svelte';
  import { getUsage } from './api';
  import UserManagement from './UserManagement.svelte';
  
  const ctx = useClerkContext();
  
  let usage: any = null;
  let userId = '';
  let animating = false;
  let showUserManagement = false;
  
  function formatTokens(tokens: number): string {
    if (tokens >= 1000000) {
      return `${(tokens / 1000000).toFixed(1)}M`;
    }
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(0)}k`;
    }
    return tokens.toString();
  }
  
  export async function refresh() {
    const token = await ctx.session?.getToken();
    if (token) {
      usage = await getUsage(token);
      
      // Trigger animation
      animating = true;
      setTimeout(() => animating = false, 300);
    }
  }
  
  onMount(async () => {
    const token = await ctx.session?.getToken();
    const user = ctx.user;
    
    if (token) {
      usage = await getUsage(token);
    }
    
    if (user?.id) {
      userId = user.id;
    }
  });
  
  $: displayedTokens = usage ? Math.min(usage.tokens_used, usage.tokens_available) : 0;
  $: tokensAvailable = usage?.tokens_available || 0;
  $: isMaxed = usage && usage.tokens_used >= usage.tokens_available;
</script>

<div class="flex items-center gap-4">
  {#if usage}
    <button
      on:click={() => showUserManagement = true}
      class="text-sm transition-all duration-300 {animating ? 'scale-110' : ''} {isMaxed ? 'text-red-400 hover:text-red-300' : 'text-gray-400 hover:text-gray-100'} cursor-pointer"
    >
      <span class="capitalize">{usage.tier}</span> ✨ 
      <span class="font-mono">{formatTokens(displayedTokens)}/{formatTokens(tokensAvailable)}</span> tokens used
    </button>
  {/if}
  <UserButton />
</div>

{#if showUserManagement}
  <UserManagement {userId} {usage} onClose={() => showUserManagement = false} />
{/if}