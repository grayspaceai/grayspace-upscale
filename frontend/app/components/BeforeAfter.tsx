'use client';
import { useRef, useState, useEffect } from 'react';
export default function BeforeAfter({ beforeSrc, afterSrc }:{ beforeSrc:string; afterSrc:string; }){
  const wrap = useRef<HTMLDivElement>(null); const [x, setX] = useState(50);
  useEffect(() => {
    const el = wrap.current!;
    const onMove = (e: MouseEvent) => { const r = el.getBoundingClientRect(); const p = Math.min(100, Math.max(0, ((e.clientX-r.left)/r.width)*100)); setX(p); };
    const down = () => window.addEventListener('mousemove', onMove); const up = () => window.removeEventListener('mousemove', onMove);
    el.addEventListener('mousedown', down); window.addEventListener('mouseup', up);
    return () => { el.removeEventListener('mousedown', down); window.removeEventListener('mouseup', up); window.removeEventListener('mousemove', onMove); };
  }, []);
  return (
    <div ref={wrap} className="slider card">
      <img src={afterSrc} alt="after"/>
      <div style={{ width: `${x}%`, overflow:'hidden', position:'absolute', inset:0 }}>
        <img src={beforeSrc} alt="before"/>
      </div>
      <div className="divider" style={{ left: `${x}%` }} />
      <div className="handle" style={{ left: `${x}%` }}>││</div>
    </div>
  );
}
