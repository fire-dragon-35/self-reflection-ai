<!-- frontend/src/lib/UserManagement.svelte -->

<script lang="ts">
  import { useClerkContext } from 'svelte-clerk/client';
  import { deleteData, deleteUser, postCreateCheckout, handleApiError } from './api';
  
  const ctx = useClerkContext();
  
  export let onClose: () => void;
  export let userId: string;
  export let usage: any;
  
  let deleting = false;
  let deletingAccount = false;
  let error = '';
  let purchasing = false;

  function formatResetDate(resetDate: string): string {
    const date = new Date(resetDate);
    date.setDate(date.getDate() + 30);
    return date.toLocaleDateString();
  }
  
  function formatTokens(tokens: number): string {
    if (tokens >= 1000000) {
      return `${(tokens / 1000000).toFixed(1)}M`;
    }
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(1)}k`;
    }
    return tokens.toString();
  }
  
  async function handleDeleteData() {
    if (!confirm('Delete all your chat history and insights?')) return;
    
    deleting = true;
    error = '';
    try {
      const token = await ctx.session?.getToken();
      await deleteData(token);
      window.location.reload();
    } catch (err) {
      const apiError = handleApiError(err);
      error = apiError.message;
    } finally {
      deleting = false;
    }
  }
  
  async function handleDeleteAccount() {
    if (!confirm('Permanently delete your account? You will be signed out.')) return;
    
    deletingAccount = true;
    error = '';
    try {
      const token = await ctx.session?.getToken();
      await deleteUser(token);
      await ctx.signOut();
    } catch (err) {
      const apiError = handleApiError(err);
      error = apiError.message;
    } finally {
      deletingAccount = false;
    }
  }
  
  async function handleBuyTokens(packageType: string) {
    purchasing = true;
    error = '';
    try {
      const token = await ctx.session?.getToken();
      const checkoutUrl = await postCreateCheckout(token, packageType);
      window.location.href = checkoutUrl;
    } catch (err) {
      const apiError = handleApiError(err);
      error = apiError.message;
    } finally {
      purchasing = false;
    }
  }
</script>

<div 
  class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" 
  on:click={onClose}
>
  <div 
    class="bg-[#151a21] border border-gray-800 rounded-lg p-4 sm:p-6 w-full max-w-sm max-h-[90vh] overflow-y-auto relative" 
    on:click|stopPropagation
  >
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold">Settings</h2>
      <button on:click={onClose} class="text-gray-400 hover:text-gray-100 text-xl">
        ✕
      </button>
    </div>
    
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
    
    <div class="space-y-2 mb-4 text-sm">
      <div class="text-gray-400">
        <span class="text-gray-500">ID:</span> <span class="font-mono text-xs">{userId}</span>
      </div>
      {#if usage}
        <div class="text-gray-400">
          <span class="text-gray-500">Tier:</span> <span class="capitalize">{usage.tier}</span>
        </div>
        <div class="text-gray-400">
          <span class="text-gray-500">Tokens available:</span> 
          <span class="font-mono">{formatTokens(usage.tokens_available)}</span>
        </div>
        <div class="text-gray-400">
          <span class="text-gray-500">Free refill (30k):</span> 
          <span>{formatResetDate(usage.tokens_reset_date)}</span>
        </div>
      {/if}
    </div>
    
    <div class="space-y-2">
      <div class="text-xs text-gray-500 mb-2">Buy Tokens</div>
      
      <button
        on:click={() => handleBuyTokens('small')}
        disabled={purchasing}
        class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm disabled:opacity-50"
      >
        🎉 200k: $2.99
      </button>
      
      <button
        on:click={() => handleBuyTokens('medium')}
        disabled={purchasing}
        class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm disabled:opacity-50"
      >
        🔥 500k: $4.99
      </button>
      
      <button
        on:click={() => handleBuyTokens('large')}
        disabled={purchasing}
        class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm disabled:opacity-50"
      >
        🚀 1M: $8.99
      </button>
      
      <div class="border-t border-gray-700 my-3"></div>
      
      <button
        on:click={handleDeleteData}
        disabled={deleting}
        class="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm disabled:opacity-50"
      >
        {deleting ? 'Deleting...' : 'Clear All Data'}
      </button>
      
      <button
        on:click={handleDeleteAccount}
        disabled={deletingAccount}
        class="w-full px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg text-sm disabled:opacity-50"
      >
        {deletingAccount ? 'Deleting...' : 'Delete Account'}
      </button>
    </div>
  </div>
</div>