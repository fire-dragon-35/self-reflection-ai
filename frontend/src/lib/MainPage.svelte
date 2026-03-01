<script lang="ts">
  import { useClerkContext } from 'svelte-clerk/client';
  import { onMount } from 'svelte';
  import { 
    getMessages, 
    postChat, 
    getAnalysis, 
    postAnalyse, 
    getSummary,
    handleApiError 
  } from './api';
  import Chat from './Chat.svelte';
  import Analysis from './Analysis.svelte';

  export let navbarRef: any;
  
  const ctx = useClerkContext();
  
  // chat state
  let message = '';
  let messages: Array<{role: string, content: string}> = [];
  let loading = false;
  let chatError = '';
  
  // insights state
  let analysis: any = null;
  let summary: string | null = null;
  let analyzing = false;
  let insightsError = '';
  
  onMount(async () => {
    const token = await ctx.session?.getToken();
    if (!token) return;
    
    messages = await getMessages(token);
    const analysisData = await getAnalysis(token);
    if (analysisData && analysisData.length > 0) {
      analysis = analysisData[0];
    }
    const summaryData = await getSummary(token);
    if (summaryData) {
      summary = summaryData;
    }
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
      const response = await postChat(token, userMessage);
      messages = [...messages, { role: 'assistant', content: response }];
      navbarRef?.refresh();
    } catch (err) {
      const apiError = handleApiError(err);
      chatError = apiError.message;
      messages = messages.slice(0, -1);
    } finally {
      loading = false;
    }
  }
  
  async function triggerAnalysis() {
    analyzing = true;
    insightsError = '';
    try {
      const token = await ctx.session?.getToken();
      const result = await postAnalyse(token);
      analysis = result.analysis;
      summary = result.summary;
      navbarRef?.refresh();
    } catch (err) {
      const apiError = handleApiError(err);
      insightsError = apiError.message;
    } finally {
      analyzing = false;
    }
  }
</script>

<main class="w-full max-w-7xl mx-auto p-3 sm:p-6">
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 w-full">
    <div class="lg:col-span-2">
      <Chat 
        {messages}
        {message}
        {loading}
        {chatError}
        onSendMessage={sendMessage}
        onMessageChange={(value) => message = value}
      />
    </div>

    <div>
      <Analysis
        {analysis}
        {summary}
        {analyzing}
        {insightsError}
        onTriggerAnalysis={triggerAnalysis}
        onClearError={() => insightsError = ''}
      />
    </div>
  </div>
</main>