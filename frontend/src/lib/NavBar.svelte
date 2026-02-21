<script lang="ts">
  import { useClerkContext, UserButton } from 'svelte-clerk/client';
  import { onMount } from 'svelte';
  import { getUsage } from './api';
  
  const ctx = useClerkContext();
  
  let usage: any = null;
  let userId = '';
  let animating = false;
  
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
      userId = user.id.slice(0, 8);
    }
  });
  
  $: displayedTokens = usage ? Math.min(usage.tokens_used, usage.tokens_limit) : 0;
  $: isMaxed = usage && usage.tokens_used >= usage.tokens_limit;
</script>

<div class="flex items-center gap-4">
  {#if usage}
    <div class="text-sm transition-all duration-300 {animating ? 'scale-110' : ''} {isMaxed ? 'text-red-400' : 'text-gray-400'}">
      <span class="capitalize">{usage.tier}</span> ✨ 
      <span class="font-mono">{displayedTokens}/{usage.tokens_limit}</span> tokens
    </div>
  {/if}
  {#if userId}
    <div class="text-xs text-gray-500">
      {userId}
    </div>
  {/if}
  <UserButton />
</div>