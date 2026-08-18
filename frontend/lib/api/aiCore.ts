import{apiFetch}from'./client';export function processAIRequest(message:string){return apiFetch('/api/ai-core/process',{method:'POST',body:JSON.stringify({message})})}
