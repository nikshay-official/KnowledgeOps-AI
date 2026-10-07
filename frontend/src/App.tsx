import { useEffect, useRef, useState } from 'react';
import { Bot, FileText, Upload, Send, ShieldCheck, Trash2, Database, Sparkles } from 'lucide-react';

const API = 'http://localhost:8000/api';
type DocumentItem = {id:number; filename:string; status:string; chunk_count:number; size_bytes:number; created_at:string};
type Citation = {document_id:number; document_name:string; chunk_id:number; page_number:number|null; score:number; snippet:string};
type Message = {role:'user'|'assistant'; content:string; citations?:Citation[]};

export default function App(){
  const [docs,setDocs]=useState<DocumentItem[]>([]);
  const [messages,setMessages]=useState<Message[]>([]);
  const [question,setQuestion]=useState('');
  const [uploading,setUploading]=useState(false);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState('');
  const fileRef=useRef<HTMLInputElement>(null);

  const loadDocs=async()=>{try{const r=await fetch(`${API}/documents`); if(!r.ok) throw new Error('Backend unavailable'); setDocs(await r.json());}catch(e:any){setError(e.message)}};
  useEffect(()=>{loadDocs()},[]);

  const upload=async(file:File)=>{
    setUploading(true); setError(''); const form=new FormData(); form.append('file',file);
    try{const r=await fetch(`${API}/documents/upload`,{method:'POST',body:form}); const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Upload failed'); await loadDocs();}
    catch(e:any){setError(e.message)} finally{setUploading(false)}
  };

  const ask=async()=>{
    const q=question.trim(); if(!q||loading) return;
    setMessages(m=>[...m,{role:'user',content:q}]); setQuestion(''); setLoading(true); setError('');
    try{const r=await fetch(`${API}/chat`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q})}); const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Request failed'); setMessages(m=>[...m,{role:'assistant',content:data.answer,citations:data.citations}]);}
    catch(e:any){setError(e.message)} finally{setLoading(false)}
  };

  const remove=async(id:number)=>{if(!confirm('Delete this document and its vectors?')) return; await fetch(`${API}/documents/${id}`,{method:'DELETE'}); loadDocs()};

  return <div className="app">
    <header className="topbar"><div className="brand"><div className="brand-icon"><Sparkles size={18}/></div><div><strong>KnowledgeOps</strong><span>AI Knowledge Assistant</span></div></div><div className="status"><span className="dot"/> RAG online</div></header>
    <main className="layout">
      <aside className="sidebar">
        <section className="side-section"><div className="section-title"><span>Knowledge base</span><span className="count">{docs.length}</span></div>
          <button className="upload" onClick={()=>fileRef.current?.click()} disabled={uploading}><Upload size={16}/>{uploading?'Indexing...':'Upload document'}</button>
          <input ref={fileRef} hidden type="file" accept=".txt,.pdf,.docx" onChange={e=>e.target.files?.[0]&&upload(e.target.files[0])}/>
          <div className="hint">PDF, DOCX or TXT · max 20 MB</div>
        </section>
        <section className="doc-list">{docs.length===0?<div className="empty-docs"><Database size={24}/><span>No documents yet</span><small>Upload a policy or product document to start.</small></div>:docs.map(d=><div className="doc" key={d.id}><div className="doc-icon"><FileText size={17}/></div><div className="doc-info"><b>{d.filename}</b><span>{d.chunk_count} chunks · {d.status}</span></div><button className="icon-btn" onClick={()=>remove(d.id)} title="Delete"><Trash2 size={14}/></button></div>)}</section>
        <div className="side-footer"><ShieldCheck size={16}/><span>Grounded answers only<br/><small>Sources are returned with every answer.</small></span></div>
      </aside>
      <section className="chat">
        <div className="chat-head"><div><h1>Ask your knowledge base</h1><p>Answers are generated from your indexed company documents.</p></div><div className="model-pill"><Bot size={15}/> Gemini RAG</div></div>
        <div className="messages">
          {messages.length===0&&<div className="welcome"><div className="welcome-icon"><Bot size={28}/></div><h2>What do you need to know?</h2><p>Ask a question about your uploaded company knowledge. The assistant will retrieve evidence and show the sources used.</p><div className="examples"><button onClick={()=>setQuestion('What is the refund policy?')}>What is the refund policy?</button><button onClick={()=>setQuestion('When can customers contact support?')}>When can customers contact support?</button><button onClick={()=>setQuestion('What are the password security requirements?')}>Password security requirements?</button></div></div>}
          {messages.map((m,i)=><div className={`message-row ${m.role}`} key={i}><div className="avatar">{m.role==='assistant'?<Bot size={15}/>:<span>Y</span>}</div><div className="bubble"><div className="content">{m.content}</div>{m.citations&&m.citations.length>0&&<div className="sources"><div className="source-label">Sources</div>{m.citations.map((c,j)=><div className="source" key={j}><FileText size={13}/><div><b>[Source {j+1}] {c.document_name}</b><span>{c.snippet}</span></div><em>{c.score.toFixed(2)}</em></div>)}</div>}</div></div>)}
          {loading&&<div className="message-row assistant"><div className="avatar"><Bot size={15}/></div><div className="bubble typing"><span/><span/><span/></div></div>}
        </div>
        {error&&<div className="error">{error}</div>}
        <div className="composer"><textarea value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();ask()}}} placeholder="Ask a question about your knowledge base..." rows={1}/><button onClick={ask} disabled={!question.trim()||loading}><Send size={17}/></button></div>
        <div className="composer-note">KnowledgeOps may decline when the knowledge base does not contain enough evidence.</div>
      </section>
    </main>
  </div>
}
