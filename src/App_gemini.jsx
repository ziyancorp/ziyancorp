import React, { useState, useEffect } from 'react';
import {

 Menu, X, Sparkles, Sun, Moon, Monitor,
 BarChart2, ShieldCheck, Zap, ChevronRight, Send,
 PieChart, TrendingUp, Briefcase, Activity, Hexagon,
 Globe, Layers
} from 'lucide-react';

// --- KOMPONEN PARTIKEL RINGAN ---
const ParticleBackground = () => {

 // Generate 30 partikel statis di awal untuk efisiensi render
 const particles = Array.from({ length: 30 }).map((_, i) => ({

   id: i,
   size: Math.random() * 3 + 1,
   left: Math.random() * 100,
   top: Math.random() * 100,
   duration: Math.random() * 20 + 10,
   delay: Math.random() * 5 * -1,
 }));

 return (
   <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
     {particles.map(p => (
      <div
        key={p.id}
        className="absolute rounded-full bg-blue-500/40 dark:bg-blue-400/30

shadow-[0_0_8px_rgba(59,130,246,0.5)] animate-float"
        style={{
          width: `${p.size}px`,
          height: `${p.size}px`,
          left: `${p.left}%`,
          top: `${p.top}%`,
          animationDuration: `${p.duration}s`,
          animationDelay: `${p.delay}s`
        }}

      />
     ))}
   </div>
 );
};

export default function App() {
 // State Tema & Navigasi
 const [themeMode, setThemeMode] = useState('system');
 const [isDark, setIsDark] = useState(false);
 const [isMenuOpen, setIsMenuOpen] = useState(false);

 // State untuk Fitur Dasbor & Kalkulator
 const [activeTab, setActiveTab] = useState('investasi');
 const [investment, setInvestment] = useState(100);

 useEffect(() => {
   const updateTheme = () => {
     if (themeMode === 'system') {
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDark(systemDark);
     } else {
      setIsDark(themeMode === 'dark');
     }
   };
   updateTheme();
   const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
   const handleChange = () => { if (themeMode === 'system') updateTheme(); };
   mediaQuery.addEventListener('change', handleChange);
   return () => mediaQuery.removeEventListener('change', handleChange);

 }, [themeMode]);

 const tabData = {
   investasi: {
     title: "Optimasi Portofolio",
     metric1: "+14.2%", desc1: "Proyeksi Alpha (Tahunan)",
     metric2: "Rendah", desc2: "Risiko Volatilitas",
     insights: ["Realokasi 15% dari obligasi ke saham teknologi disarankan.", "Lindung nilai

otomatis aktif untuk kuartal ke-4."]
   },
   bisnis: {
     title: "Efisiensi Operasional",
     metric1: "-22.5%", desc1: "Pemangkasan Biaya (CAC)",
     metric2: "1.8x", desc2: "Peningkatan Konversi (LTV)",
     insights: ["Analisis hambatan pada rantai pasok selesai.", "Otomatisasi CS mengurangi

beban tiket hingga 40%."]
   },
   pasar: {
     title: "Analisis Sentimen",
     metric1: "Bullish", desc1: "Sektor Energi Terbarukan",
     metric2: "94/100", desc2: "Skor Akurasi Prediktif",
     insights: ["Peningkatan volume institusional terdeteksi.", "Faktor makroekonomi sudah

diperhitungkan dalam harga."]
   }

 };

 return (
   <div className={`${isDark ? 'dark' : ''} min-h-screen antialiased`}>
     {/* Import Font Modern & CSS Animasi Dinamis */}
     <style dangerouslySetInnerHTML={{__html: `

      @import
url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=sw
ap');

      .font-outfit { font-family: 'Outfit', sans-serif; }
      .bg-grid-pattern {

        background-image: linear-gradient(to right, rgba(128, 128, 128, 0.05) 1px, transparent
1px),

                       linear-gradient(to bottom, rgba(128, 128, 128, 0.05) 1px, transparent 1px);
        background-size: 40px 40px;
      }
      /* Custom range slider styling */
      input[type=range]::-webkit-slider-thumb {
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.8);
      }
      /* Animasi Gradien Bergerak */
      @keyframes gradient-xy {
        0%, 100% { background-size: 400% 400%; background-position: 0% 0%; }
        25% { background-size: 400% 400%; background-position: 100% 0%; }
        50% { background-size: 400% 400%; background-position: 100% 100%; }
        75% { background-size: 400% 400%; background-position: 0% 100%; }
      }
      .animate-gradient-xy {
        animation: gradient-xy 15s ease infinite;
      }
      /* Animasi Partikel Melayang */
      @keyframes float {
        0% { transform: translateY(0px) translateX(0px); opacity: 0; }
        25% { opacity: 0.8; }
        75% { opacity: 0.8; }
        100% { transform: translateY(-200px) translateX(50px); opacity: 0; }
      }
      .animate-float {
        animation: float linear infinite;
      }
      /* Animasi Aura Ambient Lembut */
      @keyframes ambientPulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
      }
      .animate-ambient-pulse {
        animation: ambientPulse 8s ease-in-out infinite;
      }
     `}} />

     <div className="min-h-screen bg-[#f8f9fa] dark:bg-[#0c0c0d] text-slate-800
dark:text-slate-200 transition-colors duration-300 font-sans relative overflow-hidden">

      {/* === LAPISAN LATAR BELAKANG ANIMASI === */}

      <ParticleBackground />

      {/* Latar Belakang Luminous Ambient Bergerak */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-500/20
dark:bg-blue-600/15 rounded-full blur-[120px] pointer-events-none animate-ambient-pulse"
style={{ animationDelay: '0s' }}></div>
      <div className="absolute top-[30%] right-[-10%] w-[40%] h-[40%] bg-purple-500/20
dark:bg-purple-600/15 rounded-full blur-[120px] pointer-events-none animate-ambient-pulse"
style={{ animationDelay: '2s' }}></div>
      <div className="absolute bottom-[-10%] left-[20%] w-[60%] h-[40%]
bg-emerald-500/10 dark:bg-emerald-600/10 rounded-full blur-[120px] pointer-events-none
z-0 animate-ambient-pulse" style={{ animationDelay: '4s' }}></div>
      <div className="absolute inset-0 bg-grid-pattern pointer-events-none opacity-50
dark:opacity-20 z-0"></div>

      {/* NAVIGASI */}
      <nav className="fixed w-full z-50 bg-[#f8f9fa]/70 dark:bg-[#0c0c0d]/70
backdrop-blur-xl border-b border-slate-200/50 dark:border-white/5 transition-colors">

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">

           <div className="flex items-center gap-2 cursor-pointer group">
             <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400

drop-shadow-[0_0_8px_rgba(59,130,246,0.6)]
group-hover:drop-shadow-[0_0_15px_rgba(59,130,246,0.9)] transition-all duration-300" />

             <span className="font-outfit text-xl font-semibold tracking-wide text-slate-900
dark:text-white group-hover:text-transparent group-hover:bg-clip-text
group-hover:bg-gradient-to-r group-hover:from-blue-500 group-hover:to-purple-500
transition-all duration-300">

               ZYN AI Corp.
             </span>
           </div>

           <div className="hidden md:flex items-center gap-8">
             <a href="#solusi" className="font-outfit text-sm font-medium text-slate-600

dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400
hover:drop-shadow-[0_0_8px_rgba(59,130,246,0.5)] transition-all duration-300">Solusi</a>

             <a href="#simulasi" className="font-outfit text-sm font-medium text-slate-600
dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400
hover:drop-shadow-[0_0_8px_rgba(59,130,246,0.5)] transition-all duration-300">Dasbor
AI</a>

             <a href="#kalkulator" className="font-outfit text-sm font-medium text-slate-600
dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400
hover:drop-shadow-[0_0_8px_rgba(59,130,246,0.5)] transition-all duration-300">Kalkulator
ROI</a>

           </div>

           <div className="hidden md:flex items-center gap-4 relative z-10">

             <div className="flex bg-slate-200/50 dark:bg-white/5 rounded-full p-1 border
border-slate-200 dark:border-white/10 hover:shadow-[0_0_10px_rgba(255,255,255,0.1)]
transition-all">

               <button onClick={() => setThemeMode('light')} className={`p-1.5 rounded-full
transition-all ${themeMode === 'light' ? 'bg-white dark:bg-slate-700
shadow-[0_0_8px_rgba(0,0,0,0.1)] text-slate-900 dark:text-white' : 'text-slate-500
hover:text-slate-700 dark:hover:text-slate-300'}`}><Sun className="w-4 h-4" /></button>

               <button onClick={() => setThemeMode('system')} className={`p-1.5 rounded-full
transition-all ${themeMode === 'system' ? 'bg-white dark:bg-slate-700
shadow-[0_0_8px_rgba(0,0,0,0.1)] text-slate-900 dark:text-white' : 'text-slate-500
hover:text-slate-700 dark:hover:text-slate-300'}`}><Monitor className="w-4 h-4"
/></button>

               <button onClick={() => setThemeMode('dark')} className={`p-1.5 rounded-full
transition-all ${themeMode === 'dark' ? 'bg-white dark:bg-[#3f3f46]
shadow-[0_0_8px_rgba(255,255,255,0.1)] text-slate-900 dark:text-white' : 'text-slate-500
hover:text-slate-700 dark:hover:text-slate-300'}`}><Moon className="w-4 h-4" /></button>

             </div>
             <button className="font-outfit px-5 py-2 text-sm font-medium bg-slate-900
dark:bg-white text-white dark:text-slate-900 rounded-full
hover:shadow-[0_0_15px_rgba(59,130,246,0.4)]
dark:hover:shadow-[0_0_20px_rgba(255,255,255,0.6)] hover:-translate-y-0.5 transition-all
duration-300 relative overflow-hidden group">

               <span className="relative z-10">Mulai Analisis</span>
               {/* Efek gradien bergerak di tombol saat hover */}
               <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600
to-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300
animate-gradient-xy"></div>
             </button>
           </div>

           <div className="md:hidden flex items-center gap-4">
             <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="text-slate-600

dark:text-slate-300 hover:drop-shadow-[0_0_8px_rgba(255,255,255,0.5)]">
               {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}

             </button>
           </div>
          </div>
        </div>

        {/* DROP-DOWN MENU MOBILE */}
        {isMenuOpen && (

          <div className="md:hidden bg-white/95 dark:bg-[#121214]/95 backdrop-blur-xl
border-b border-slate-200 dark:border-white/10 px-4 py-6 space-y-4
shadow-[0_20px_40px_rgba(0,0,0,0.2)] absolute w-full">

           <div className="flex flex-col space-y-4 mb-6">
             <a onClick={() => setIsMenuOpen(false)} href="#solusi" className="font-outfit

text-base font-medium text-slate-700 dark:text-slate-200 hover:text-blue-500">Solusi
Bisnis</a>

             <a onClick={() => setIsMenuOpen(false)} href="#simulasi" className="font-outfit
text-base font-medium text-slate-700 dark:text-slate-200 hover:text-blue-500">Dasbor
AI</a>

             <a onClick={() => setIsMenuOpen(false)} href="#kalkulator"
className="font-outfit text-base font-medium text-slate-700 dark:text-slate-200
hover:text-blue-500">Kalkulator ROI</a>

           </div>
           <button className="font-outfit w-full mt-4 px-5 py-3 text-sm font-medium
bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full
shadow-[0_0_15px_rgba(59,130,246,0.3)] animate-gradient-xy">

             Mulai Analisis
           </button>
          </div>
        )}
      </nav>

      {/* HERO SECTION */}
      <section className="relative pt-32 pb-12 sm:pt-40 sm:pb-16 px-4 flex flex-col
items-center justify-center text-center z-10">

        <div className="max-w-4xl mx-auto space-y-8">
          <h1 className="font-outfit text-5xl sm:text-6xl lg:text-7xl font-light tracking-tighter

text-slate-900 dark:text-white leading-[1.1]">
           Kecerdasan untuk<br/>
           {/* Teks Gradien Bergerak */}
           <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r

from-blue-500 via-purple-500 to-emerald-500 animate-gradient-xy
drop-shadow-[0_0_20px_rgba(147,51,234,0.3)]
dark:drop-shadow-[0_0_30px_rgba(147,51,234,0.6)]">

             Eksekusi Bisnis.
           </span>
          </h1>

          <p className="font-outfit text-lg sm:text-xl font-light text-slate-600
dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">

           ZYN AI Corp menghadirkan infrastruktur data analitik yang mengubah metrik
mentah menjadi strategi bisnis dan investasi yang siap dieksekusi detik ini juga.

          </p>

          {/* REACTIVE LUMINOUS INPUT */}
          <div className="mt-12 max-w-2xl mx-auto relative z-20">

           <div className="relative group">
             <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 via-purple-500

to-emerald-500 animate-gradient-xy rounded-[2.5rem] blur-xl opacity-40
group-hover:opacity-100 group-hover:blur-2xl group-focus-within:opacity-100
group-focus-within:blur-2xl transition-all duration-700"></div>

             <div className="relative flex items-center bg-white/95 dark:bg-[#121214]/90
backdrop-blur-md border border-slate-200/50 dark:border-white/10 rounded-[2.5rem] p-2
shadow-2xl transition-all">

               <div className="pl-5 pr-2">
                <Sparkles className="w-5 h-5 text-blue-500 dark:text-blue-400

drop-shadow-[0_0_8px_rgba(59,130,246,0.6)] group-focus-within:animate-pulse" />
               </div>
               <input
                type="text"
                placeholder="Analisis laporan keuangan Q3 untuk efisiensi margin..."
                className="font-outfit w-full bg-transparent border-none focus:outline-none

text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 py-3.5
text-base"

               />
               <button className="bg-slate-900 dark:bg-white text-white dark:text-slate-900
p-3.5 rounded-full hover:shadow-[0_0_20px_rgba(59,130,246,0.8)] transition-all
duration-300 flex-shrink-0 relative overflow-hidden group/btn">

                <span className="relative z-10"><Send className="w-5 h-5" /></span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600
opacity-0 group-hover/btn:opacity-100 group-focus-within:opacity-100 transition-opacity
duration-300 text-white"></div>
               </button>
             </div>
           </div>
          </div>
        </div>
      </section>

      {/* TRUSTED BY */}
      <section className="py-8 border-y border-slate-200/50 dark:border-white/5
bg-white/30 dark:bg-black/20 backdrop-blur-sm relative z-10 mt-4">

        <div className="max-w-7xl mx-auto px-4 flex flex-col items-center">
          <p className="font-outfit text-xs font-medium text-slate-500 dark:text-slate-400

uppercase tracking-widest mb-6">Infrastruktur AI Dipercaya Oleh</p>
          <div className="flex flex-wrap justify-center items-center gap-8 sm:gap-16

opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
           <div className="flex items-center gap-2 font-outfit font-bold text-xl text-slate-800

dark:text-white hover:drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]"><Hexagon
className="w-6 h-6"/> Nexus Cap</div>

           <div className="flex items-center gap-2 font-outfit font-bold text-xl text-slate-800
dark:text-white hover:drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]"><Globe
className="w-6 h-6"/> GlobalNet</div>

           <div className="flex items-center gap-2 font-outfit font-bold text-xl text-slate-800
dark:text-white hover:drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]"><Layers
className="w-6 h-6"/> Synthetix</div>

          </div>
        </div>
      </section>

      {/* DASBOR INTERAKTIF */}
      <section id="simulasi" className="py-20 px-4 relative z-10">

        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
           <h2 className="font-outfit text-3xl sm:text-4xl font-medium text-slate-900

dark:text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.1)]">Dasbor Analitik
Real-Time</h2>

           <p className="font-outfit text-slate-500 dark:text-slate-400 mt-3">Simulasi
pengolahan data mentah menjadi wawasan bisnis.</p>

          </div>

          <div className="relative group">
           <div className="absolute -inset-[1px] bg-gradient-to-r from-blue-500/40

via-purple-500/40 to-emerald-500/40 animate-gradient-xy rounded-[25px] opacity-0
group-hover:opacity-100 transition-opacity duration-700 blur-md"></div>

           <div className="relative bg-white/90 dark:bg-[#18181a]/90 backdrop-blur-2xl
border border-slate-200 dark:border-white/10 rounded-[24px] overflow-hidden shadow-2xl">

             <div className="flex flex-col sm:flex-row border-b border-slate-200
dark:border-white/10 bg-slate-50/50 dark:bg-[#1e1e20]/80">

               <button onClick={() => setActiveTab('investasi')} className={`font-outfit flex
items-center justify-center gap-2 px-6 py-5 font-medium text-sm transition-all duration-300
flex-1 ${activeTab === 'investasi' ? 'border-b-2 border-blue-500 text-blue-600
dark:text-blue-400 bg-white dark:bg-[#18181a]
drop-shadow-[0_0_10px_rgba(59,130,246,0.4)]' : 'text-slate-500 hover:text-slate-700
dark:hover:text-slate-300 hover:bg-white/50 dark:hover:bg-white/5'}`}>

                <PieChart className="w-4 h-4" /> Portofolio Investasi
               </button>
               <button onClick={() => setActiveTab('bisnis')} className={`font-outfit flex
items-center justify-center gap-2 px-6 py-5 font-medium text-sm transition-all duration-300
flex-1 ${activeTab === 'bisnis' ? 'border-b-2 border-purple-500 text-purple-600
dark:text-purple-400 bg-white dark:bg-[#18181a]
drop-shadow-[0_0_10px_rgba(168,85,247,0.4)]' : 'text-slate-500 hover:text-slate-700
dark:hover:text-slate-300 hover:bg-white/50 dark:hover:bg-white/5'}`}>

                <Briefcase className="w-4 h-4" /> Efisiensi Bisnis
               </button>
               <button onClick={() => setActiveTab('pasar')} className={`font-outfit flex
items-center justify-center gap-2 px-6 py-5 font-medium text-sm transition-all duration-300
flex-1 ${activeTab === 'pasar' ? 'border-b-2 border-emerald-500 text-emerald-600
dark:text-emerald-400 bg-white dark:bg-[#18181a]
drop-shadow-[0_0_10px_rgba(16,185,129,0.4)]' : 'text-slate-500 hover:text-slate-700
dark:hover:text-slate-300 hover:bg-white/50 dark:hover:bg-white/5'}`}>

                <TrendingUp className="w-4 h-4" /> Analisis Pasar
               </button>
             </div>

             <div className="p-8 sm:p-10">
               <div className="flex items-center gap-3 mb-8">
                <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse

shadow-[0_0_12px_rgba(34,197,94,0.9)]"></div>
                <span className="font-outfit text-xs font-semibold text-slate-500

dark:text-slate-400 uppercase tracking-widest
drop-shadow-[0_0_5px_rgba(255,255,255,0.1)]">Status: Sinkronisasi Aktif ·
{tabData[activeTab].title}</span>

               </div>

               <div className="grid md:grid-cols-2 gap-10">
                <div className="space-y-6">
                  <div className="bg-white dark:bg-[#131314] p-6 rounded-2xl border

border-slate-200 dark:border-white/5 hover:border-blue-500/40
hover:shadow-[0_0_30px_rgba(59,130,246,0.15)] transition-all duration-500 group/card">

                    <div className="font-outfit text-5xl font-light tracking-tighter text-slate-900
dark:text-white mb-2 group-hover/card:drop-shadow-[0_0_15px_rgba(25