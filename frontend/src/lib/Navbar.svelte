<!-- frontend/src/lib/Navbar.svelte -->

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
      return `${(tokens / 1000).toFixed(1)}k`;
    }
    return tokens.toString();
  }
  
  export async function refresh() {
    const token = await ctx.session?.getToken();
    if (token) {
      usage = await getUsage(token);
      
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
</script>

<div class="flex items-center gap-2 sm:gap-4">
  {#if usage}
    <button
      on:click={() => showUserManagement = true}
      class="text-xs sm:text-sm transition-all duration-300 {animating ? 'scale-110' : ''} {usage.tokens_available == 0 ? 'text-red-400 hover:text-red-300' : 'text-gray-400 hover:text-gray-100'} cursor-pointer"
    >
      <span class="hidden sm:inline capitalize">{usage.tier}</span>
      <span class="hidden sm:inline">✨</span>
      <span class="font-mono">{formatTokens(usage.tokens_available)}</span>
      <span class="hidden sm:inline">tokens</span>
    </button>
  {/if}
  <UserButton />
</div>

{#if showUserManagement}
  <UserManagement {userId} {usage} onClose={() => showUserManagement = false} />
{/if}