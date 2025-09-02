'use client';
import { useState } from 'react';
import BeforeAfter from '../components/BeforeAfter';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export default function Page(){
  const [file, setFile] = useState<File|null>(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{before:string; after:string;}|null>(null);
  const [scale, setScale] = useState(2);
  async function onSubmit(e: React.FormEvent){
    e.preventDefault(); if(!file) return; setBusy(true); setResult(null);
    const form = new FormData(); form.append('file', file); form.append('scale', String(scale));
    const res = await fetch(`${API_URL}/upscale`, { method:'POST', body: form });
    if(!res.ok){ alert('업로드 실패'); setBusy(false); return; }
    const data = await res.json();
    const before = data.before.startsWith('http')? data.before : `${API_URL}${data.before}`;
    const after  = data.after.startsWith('http')? data.after  : `${API_URL}${data.after}`;
    setResult({ before, after }); setBusy(false);
  }
  return (
    <div>
      <h1 style={{marginBottom:8}}>GraySpace Upscale</h1>
      <p className="hint">2D 이미지를 고해상도로 업스케일하고, 바 슬라이더로 전/후를 비교하세요.</p>
      <div className="card" style={{marginTop:16}}>
        <form onSubmit={onSubmit}>
          <input type="file" accept="image/*" onChange={e=> setFile(e.target.files?.[0]||null)} />
          <select value={scale} onChange={e=> setScale(parseInt(e.target.value))} style={{margin:'0 12px'}}>
            <option value={2}>x2</option><option value={4}>x4</option>
          </select>
          <button className="btn" disabled={!file || busy}>{busy? '처리중…' : 'Upscale'}</button>
        </form>
      </div>
      {result && (
        <div style={{marginTop:20}}>
          <BeforeAfter beforeSrc={result.before} afterSrc={result.after} />
          <div style={{marginTop:8}}><a className="btn" href={result.after} download>결과 다운로드</a></div>
        </div>
      )}
    </div>
  );
}
