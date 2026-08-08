import React, { useState, useEffect } from 'react';
import {
  Menu, X, Sparkles, Sun, Moon, Monitor,
  BarChart2, ShieldCheck, Zap, ChevronRight, Send,
  PieChart, TrendingUp, Briefcase, Activity, Hexagon,
  Globe, Layers, Search, Bot, Target, CheckCircle2
} from 'lucide-react';

// --- KOMPONEN PARTIKEL RINGAN ---
const ParticleBackground = () => {
  const particles = Array.from({ length: 30 }).map((_, i) => ({
    id: i, size: Math.random() * 3 + 1, left: Math.random() * 100,
    top: Math.random() * 100, duration: Math.random() * 20 + 10, delay: Math.random() * 5 * -1,
  }));
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
      {particles.map(p => (
        <div key={p.id} className="absolute rounded-full bg-blue-500/40 dark:bg-blue-400/30 shadow-[0_0_8px_rgba(59,130,246,0.5)] animate-float"
          style={{ width: `${p.size}px`, height: `${p.size}px`, left: `${p.left}%`, top: `${p.top}%`, animationDuration: `${p.duration}s`, animationDelay: `${p.delay}s` }} />
      ))}
    </div>
  );
};

export default function App() {
  const [themeMode, setThemeMode] = useState('system');
  const [isDark, setIsDark] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const updateTheme = () => {
      if (themeMode === 'system') setIsDark(window.matchMedia('(prefers-color-scheme: dark)').matches);
      else setIsDark(themeMode === 'dark');
    };
    updateTheme();
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', () => { if (themeMode === 'system') updateTheme(); });
    return () => mq.removeEventListener('change', () => {});
  }, [themeMode]);

  const products = [
    { icon: Zap, title: 'Auto-Affiliate', desc: 'Kirim video/foto + link Shopee ke Telegram → otomatis post FB + YouTube + X. 2 mode: langsung (77 mnt) atau terpusat via Google Sheet (53/67 mnt).', tags: ['Shopee', 'FB', 'YouTube', 'X'] },
    { icon: Bot, title: 'AI CS Bot', desc: 'Customer service Telegram otomatis berbasis 9router. Paham sales, marketing, closing. Catat keluhan ke CSV untuk analisis.', tags: ['Telegram', 'Sales', 'Closing'] },
    { icon: Target, title: 'Job Hunter', desc: 'Agent AI pantau job board 24/7, filter lowongan cocok vs CV, kirim rekomendasi ke Telegram. Trial 3 hari.', tags: ['Lowongan', 'CV', 'AI Filter'] },
  ];

  const steps = [
    'Fork / clone repo ZIYAN Templates dari GitHub',
    'Isi .env.example dengan token kamu (FB, YouTube, Google, 9router)',
    'Jalankan: python scheduler.py loop (atau import workflow n8n)',
    'Kirim bahan ke Telegram → sistem otomatis posting & arsip',
  ];

  return (
    <div className={`${isDark ? 'dark' : ''} min-h-screen antialiased`}>
      <style dangerouslySetInnerHTML={{__html: `
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        .font-outfit { font-family: 'Outfit', sans-serif; }
        .bg-grid-pattern { background-image: linear-gradient(to right, rgba(128,128,128,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(128,128,128,0.05) 1px, transparent 1px); background-size: 40px 40px; }
        input[type=range]::-webkit-slider-thumb { box-shadow: 0 0 15px rgba(59,130,246,0.8); }
        @keyframes gradient-xy { 0%,100% { background-size: 400% 400%; background-position: 0% 0%; } 25% { background-size: 400% 400%; background-position: 100% 0%; } 50% { background-size: 400% 400%; background-position: 100% 100%; } 75% { background-size: 400% 400%; background-position: 0% 100%; } }
        .animate-gradient-xy { animation: gradient-xy 15s ease infinite; }
        @keyframes float { 0% { transform: translateY(0) translateX(0); opacity: 0; } 25% { opacity: 0.8; } 75% { opacity: 0.8; } 100% { transform: translateY(-200px) translateX(50px); opacity: 0; } }
        .animate-float { animation: float linear infinite; }
        @keyframes ambientPulse { 0%,100% { transform: scale(1); opacity: 0.5; } 50% { transform: scale(1.1); opacity: 0.8; } }
        .animate-ambient-pulse { animation: ambientPulse 8s ease-in-out infinite; }
      `}} />

      <div className="min-h-screen bg-[#f8f9fa] dark:bg-[#0c0c0d] text-slate-800 dark:text-slate-200 transition-colors duration-300 font-sans relative overflow-hidden">
        <ParticleBackground />
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-500/20 dark:bg-blue-600/15 rounded-full blur-[120px] pointer-events-none animate-ambient-pulse" style={{ animationDelay: '0s' }}></div>
        <div className="absolute top-[30%] right-[-10%] w-[40%] h-[40%] bg-purple-500/20 dark:bg-purple-600/15 rounded-full blur-[120px] pointer-events-none animate-ambient-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-[-10%] left-[20%] w-[60%] h-[40%] bg-emerald-500/10 dark:bg-emerald-600/10 rounded-full blur-[120px] pointer-events-none z-0 animate-ambient-pulse" style={{ animationDelay: '4s' }}></div>
        <div className="absolute inset-0 bg-grid-pattern pointer-events-none opacity-50 dark:opacity-20 z-0"></div>

        {/* NAVIGASI */}
        <nav className="fixed w-full z-50 bg-[#f8f9fa]/70 dark:bg-[#0c0c0d]/70 backdrop-blur-xl border-b border-slate-200/50 dark:border-white/5 transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-2 cursor-pointer group">
                <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400 drop-shadow-[0_0_8px_rgba(59,130,246,0.6)] group-hover:drop-shadow-[0_0_15px_rgba(59,130,246,0.9)] transition-all duration-300" />
                <span className="font-outfit text-xl font-semibold tracking-wide text-slate-900 dark:text-white">ZYN AI Corp.</span>
              </div>
              <div className="hidden md:flex items-center gap-8">
                <a href="#produk" className="font-outfit text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-all">Produk</a>
                <a href="#cara" className="font-outfit text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-all">Cara Pakai</a>
                <a href="#templates" className="font-outfit text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-all">Templates</a>
                <a href="#job-hunter" className="font-outfit text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition-all">Job Hunter</a>
              </div>
              <div className="hidden md:flex items-center gap-4 relative z-10">
                <div className="flex bg-slate-200/50 dark:bg-white/5 rounded-full p-1 border border-slate-200 dark:border-white/10">
                  <button onClick={() => setThemeMode('light')} className={`p-1.5 rounded-full transition-all ${themeMode === 'light' ? 'bg-white dark:bg-slate-700 shadow-[0_0_8px_rgba(0,0,0,0.1)] text-slate-900 dark:text-white' : 'text-slate-500'}`}><Sun className="w-4 h-4" /></button>
                  <button onClick={() => setThemeMode('system')} className={`p-1.5 rounded-full transition-all ${themeMode === 'system' ? 'bg-white dark:bg-slate-700 shadow-[0_0_8px_rgba(0,0,0,0.1)] text-slate-900 dark:text-white' : 'text-slate-500'}`}><Monitor className="w-4 h-4" /></button>
                  <button onClick={() => setThemeMode('dark')} className={`p-1.5 rounded-full transition-all ${themeMode === 'dark' ? 'bg-white dark:bg-[#3f3f46] shadow-[0_0_8px_rgba(255,255,255,0.1)] text-slate-900 dark:text-white' : 'text-slate-500'}`}><Moon className="w-4 h-4" /></button>
                </div>
                <a href="https://t.me/Employeezynbot" className="font-outfit px-5 py-2 text-sm font-medium bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full hover:shadow-[0_0_15px_rgba(59,130,246,0.4)] transition-all duration-300">Chat CS</a>
              </div>
              <div className="md:hidden flex items-center gap-4">
                <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-slate-600 dark:text-slate-300">{isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}</button>
              </div>
            </div>
          </div>
          {isMenuOpen && (
            <div className="md:hidden bg-white/95 dark:bg-[#121214]/95 backdrop-blur-xl border-b border-slate-200 dark:border-white/10 px-4 py-6 space-y-4 shadow-[0_20px_40px_rgba(0,0,0,0.2)] absolute w-full">
              <a onClick={() => setIsMenuOpen(false)} href="#produk" className="font-outfit text-base font-medium text-slate-700 dark:text-slate-200 block">Produk</a>
              <a onClick={() => setIsMenuOpen(false)} href="#cara" className="font-outfit text-base font-medium text-slate-700 dark:text-slate-200 block">Cara Pakai</a>
              <a onClick={() => setIsMenuOpen(false)} href="#templates" className="font-outfit text-base font-medium text-slate-700 dark:text-slate-200 block">Templates</a>
              <a onClick={() => setIsMenuOpen(false)} href="#job-hunter" className="font-outfit text-base font-medium text-slate-700 dark:text-slate-200 block">Job Hunter</a>
            </div>
          )}
        </nav>

        {/* HERO */}
        <section className="relative pt-32 pb-12 sm:pt-40 sm:pb-16 px-4 flex flex-col items-center justify-center text-center z-10">
          <div className="max-w-4xl mx-auto space-y-8">
            <h1 className="font-outfit text-5xl sm:text-6xl lg:text-7xl font-light tracking-tighter text-slate-900 dark:text-white leading-[1.1]">
              Otomasi Bisnis<br/>
              <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 via-purple-500 to-emerald-500 animate-gradient-xy drop-shadow-[0_0_20px_rgba(147,51,234,0.3)]">Dikelola AI.</span>
            </h1>
            <p className="font-outfit text-lg sm:text-xl font-light text-slate-600 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
              ZYN AI Corp membangun sistem affiliate otomatis, CS bot Telegram, dan Job Hunter — semua siap pakai, tinggal hubungkan token kamu.
            </p>
            <div className="flex flex-wrap justify-center gap-4 mt-8">
              <a href="#templates" className="font-outfit px-6 py-3 text-sm font-medium bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-full hover:shadow-[0_0_20px_rgba(59,130,246,0.6)] transition-all">Ambil Template</a>
              <a href="https://t.me/Employeezynbot" className="font-outfit px-6 py-3 text-sm font-medium border border-slate-300 dark:border-white/20 rounded-full hover:shadow-[0_0_15px_rgba(59,130,246,0.3)] transition-all">Tanya CS AI</a>
            </div>
          </div>
        </section>

        {/* PRODUK */}
        <section id="produk" className="py-20 px-4 relative z-10">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-outfit text-3xl sm:text-4xl font-medium text-slate-900 dark:text-white">Produk ZIYAN</h2>
              <p className="font-outfit text-slate-500 dark:text-slate-400 mt-3">Tiga sistem yang sudah berjalan — bukan konsep.</p>
            </div>
            <div className="grid md:grid-cols-3 gap-6">
              {products.map((p, i) => (
                <div key={i} className="bg-white/90 dark:bg-[#131314]/90 backdrop-blur-xl p-8 rounded-2xl border border-slate-200 dark:border-white/5 hover:border-blue-500/40 hover:shadow-[0_0_40px_rgba(59,130,246,0.12)] transition-all duration-500">
                  <p.icon className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-5 drop-shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
                  <h3 className="font-outfit text-xl font-medium text-slate-900 dark:text-white mb-3">{p.title}</h3>
                  <p className="font-outfit text-sm font-light text-slate-600 dark:text-slate-400 leading-relaxed mb-4">{p.desc}</p>
                  <div className="flex flex-wrap gap-2">
                    {p.tags.map((t, j) => <span key={j} className="text-xs font-outfit px-2 py-1 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400">{t}</span>)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CARA PAKAI */}
        <section id="cara" className="py-20 px-4 relative z-10 bg-white/30 dark:bg-black/20 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-outfit text-3xl sm:text-4xl font-medium text-slate-900 dark:text-white">Cara Pakai</h2>
              <p className="font-outfit text-slate-500 dark:text-slate-400 mt-3">Dari clone sampai live dalam 10 menit.</p>
            </div>
            <div className="space-y-4">
              {steps.map((s, i) => (
                <div key={i} className="flex items-start gap-4 bg-white/90 dark:bg-[#131314]/90 backdrop-blur-xl p-5 rounded-2xl border border-slate-200 dark:border-white/5">
                  <div className="w-8 h-8 rounded-full bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center font-outfit font-semibold text-sm shrink-0">{i+1}</div>
                  <p className="font-outfit text-sm font-light text-slate-700 dark:text-slate-300">{s}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* TEMPLATES */}
        <section id="templates" className="py-20 px-4 relative z-10">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-outfit text-3xl sm:text-4xl font-medium text-slate-900 dark:text-white">Template Siap Pakai</h2>
              <p className="font-outfit text-slate-500 dark:text-slate-400 mt-3">Otomasi ZIYAN yang sudah berjalan — tinggal isi token, langsung jalan.</p>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { t: 'Auto-Affiliate v1 (Mode Langsung)', d: '1 file+1 link ke Telegram → post FB+YT+X tiap 77 mnt. Kontrol manual, simpel.', l: 'https://raw.githubusercontent.com/yangmulia96/ziyancorp/main/ZIYAN_TEMPLATES/affiliate/scheduler_v1_legacy.py' },
                { t: 'Auto-Affiliate v2 (Mode Sheet)', d: 'Kirim banyak → masuk Google Sheet → sync 53 mnt → publish 67 mnt. Anti-spam, terpusat.', l: 'https://raw.githubusercontent.com/yangmulia96/ziyancorp/main/ZIYAN_TEMPLATES/affiliate/scheduler.py' },
                { t: 'AI CS Bot Kit', d: 'Bot Telegram jawab otomatis (sales/closing), log keluhan ke CSV. Pakai 9router kr/auto.', l: 'https://raw.githubusercontent.com/yangmulia96/ziyancorp/main/ZIYAN_TEMPLATES/cs_bot/ziyan_corp_cs_bot.py' },
                { t: 'Job Hunter Kit', d: 'Workflow n8n cari lowongan via JSearch, filter skor, kirim ke Telegram. Siap import.', l: 'https://raw.githubusercontent.com/yangmulia96/ziyancorp/main/ZIYAN_TEMPLATES/job_hunter/ziyan_job_hunter.json' },
              ].map((x, i) => (
                <div key={i} className="bg-white/90 dark:bg-[#131314]/90 backdrop-blur-xl p-6 rounded-2xl border border-slate-200 dark:border-white/5 hover:border-blue-500/40 hover:shadow-[0_0_30px_rgba(59,130,246,0.12)] transition-all duration-500 flex flex-col">
                  <h3 className="font-outfit text-lg font-medium text-slate-900 dark:text-white mb-2">{x.t}</h3>
                  <p className="font-outfit text-sm font-light text-slate-600 dark:text-slate-400 leading-relaxed mb-4 flex-1">{x.d}</p>
                  <a href={x.l} className="font-outfit inline-flex items-center justify-center gap-2 w-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-4 py-2.5 rounded-full font-medium text-sm hover:shadow-[0_0_20px_rgba(59,130,246,0.6)] transition-all duration-300">Ambil Template <ChevronRight className="w-4 h-4" /></a>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* JOB HUNTER */}
        <section id="job-hunter" className="py-20 px-4 relative z-10 bg-white/30 dark:bg-black/20 backdrop-blur-sm">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="font-outfit text-3xl sm:text-4xl font-medium text-slate-900 dark:text-white">AI Job Hunter</h2>
              <p className="font-outfit text-slate-500 dark:text-slate-400 mt-3">Tim agent AI carikan lowongan cocok tiap hari ke HP kamu.</p>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              {[
                { icon: Search, title: 'Pantau 24/7', desc: 'Agent AI scan job board tiap hari, filter yang relevan vs CV kamu.' },
                { icon: BarChart2, title: 'Skor Kecocokan', desc: 'Tiap lowongan dapat skor similarity — cuma yang di atas threshold yang dikirim.' },
                { icon: Bot, title: 'Kirim ke Telegram', desc: 'Rekomendasi mendarat di chat kamu, lengkap dengan link lamaran.' },
                { icon: CheckCircle2, title: 'Trial 3 Hari', desc: 'Coba gratis dulu. Berlangganan Rp99rb/bln, cancel kapan saja.' },
              ].map((f, idx) => (
                <div key={idx} className="bg-white/90 dark:bg-[#131314]/90 backdrop-blur-xl p-8 rounded-2xl border border-slate-200 dark:border-white/5 hover:border-blue-500/40 hover:shadow-[0_0_40px_rgba(59,130,246,0.12)] transition-all duration-500">
                  <f.icon className="w-8 h-8 text-blue-600 dark:text-blue-400 mb-5" />
                  <h3 className="font-outfit text-xl font-medium text-slate-900 dark:text-white mb-3">{f.title}</h3>
                  <p className="font-outfit text-sm font-light text-slate-600 dark:text-slate-400 leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
            <div className="bg-white/90 dark:bg-[#18181a]/90 backdrop-blur-2xl border border-slate-200 dark:border-white/10 rounded-[2rem] p-10 sm:p-14 mt-8">
              <div className="grid md:grid-cols-2 gap-10 items-center">
                <div>
                  <h3 className="font-outfit text-2xl font-light text-slate-900 dark:text-white mb-5">Paket Berlangganan</h3>
                  <ul className="space-y-3">
                    {['Pantauan job board harian otomatis','Filter AI cocok dengan CV kamu','Laporan mingguan via Telegram','Tips & kata kunci lolos ATS'].map((item, i) => (
                      <li key={i} className="flex items-start gap-3 font-outfit text-sm font-light text-slate-600 dark:text-slate-300"><CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />{item}</li>
                    ))}
                  </ul>
                </div>
                <div className="bg-gradient-to-br from-blue-500/10 to-emerald-500/10 rounded-2xl p-8 border border-blue-500/20 text-center">
                  <p className="font-outfit text-sm text-slate-500 dark:text-slate-400 mb-1">Mulai dari</p>
                  <p className="font-outfit text-4xl font-semibold text-slate-900 dark:text-white mb-1">Rp99.000<span className="text-base font-light">/bln</span></p>
                  <p className="font-outfit text-xs text-slate-500 dark:text-slate-400 mb-6">Cancel kapan saja</p>
                  <a href="https://t.me/Employeezynbot" className="font-outfit inline-flex items-center justify-center gap-2 w-full bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-6 py-3 rounded-full font-medium hover:shadow-[0_0_30px_rgba(59,130,246,0.7)] transition-all duration-300">Daftar Sekarang <ChevronRight className="w-4 h-4" /></a>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="relative z-10 border-t border-slate-200/50 dark:border-white/5 bg-white/40 dark:bg-black/30 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 py-10 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span className="font-outfit text-sm font-semibold text-slate-900 dark:text-white">ZYN AI Corp.</span>
            </div>
            <p className="font-outfit text-xs text-slate-500 dark:text-slate-400">© {new Date().getFullYear()} ZYN AI Corp. Dijalankan sepenuhnya oleh AI agent.</p>
          </div>
        </footer>
      </div>
    </div>
  );
}
